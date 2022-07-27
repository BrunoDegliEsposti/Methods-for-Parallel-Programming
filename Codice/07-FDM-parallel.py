import os, sys, time
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
from numpy import pi
from mpi4py import MPI

# Get communicator information
# https://mpi4py.readthedocs.io/en/stable/reference/mpi4py.MPI.Comm.html
comm = MPI.COMM_WORLD
nprocesses = comm.Get_size()
rank = comm.Get_rank()
if rank == 0:
	rank_left = MPI.PROC_NULL
else:
	rank_left = rank - 1
if rank == nprocesses - 1:
	rank_right = MPI.PROC_NULL
else:
	rank_right = rank + 1

# Define parameters of the numerical method
argc = len(sys.argv)
if argc > 1:
	N_global = int(sys.argv[1])
else:
	N_global = 40000
if argc > 2:
	tol = float(sys.argv[2])
else:
	tol = 1e-12
if argc > 3:
	W = int(sys.argv[3])
else:
	W = 256
if argc > 4:
	filename = sys.argv[4]
else:
	filename = "results.txt"

# Define problem -u_xx = f
xL = 0
xR = 1
sigma = lambda x: 1/(1+x*x)
f = lambda x: (pi*pi + 1/(1+x*x)) * np.sin(pi*x)
u_exact = lambda x: np.sin(pi*x)
uL = u_exact(xL)
uR = u_exact(xR)

# Discretize the domain [xL,xR]
# N_global: total number of unknowns (without boundary)
# N_local: number of unknowns per process (without halos)
# N: number of unknowns per process (with left and right halos)
# W: width of halo
N_global -= N_global % nprocesses
N_local = N_global // nprocesses
h = (xR-xL)/(N_global+1)
x_with_boundary = np.linspace(xL,xR,N_global+2)
x_global = x_with_boundary[1:-1]
x_local = x_global[N_local*rank:N_local*(rank+1)]
if rank == 0:
	W_left = 0
else:
	W_left = W
if rank == nprocesses-1:
	W_right = 0
else:
	W_right = W
N = W_left + N_local + W_right
x = x_global[N_local*rank-W_left:N_local*(rank+1)+W_right]

# Initialize starting point of conjugate gradient as the
# line interpolating boundary conditions. Initialize rhs.
slope = (uR-uL)/(xR-xL)
u = slope*(x-xL)+uL
b = f(x)
if rank == 0:
	b[0] += uL/(h*h)
if rank == nprocesses-1:
	b[-1] += uR/(h*h)

# Initialize the residual r=b-Au and the vectors p,v
stencil = np.array([-1/(h*h), 2/(h*h), -1/(h*h)])
sigma_x = sigma(x)
r = f(x)
p = r.copy()
v = np.zeros(p.shape)

# Also initialize local (i.e. non overlapping) views
# The None trick is used when W_right==0
u_local = u[W_left:-W_right or None]
b_local = b[W_left:-W_right or None]
r_local = r[W_left:-W_right or None]
p_local = p[W_left:-W_right or None]
v_local = v[W_left:-W_right or None]

# Initialize memory for dot products
bb_global = np.zeros(1)
rr_global = np.zeros(1)
pv_global = np.zeros(1)
bb_local = np.vdot(b_local,b_local)
comm.Allreduce(bb_local, bb_global, op=MPI.SUM)

# Define routine for halo exchange
def halo_exchange(v):
	# Left halos are refilled: data is sent to the right
	sendbuf = v[-2*W_right:-W_right]
	recvbuf = v[0:W_left]
	comm.Sendrecv(sendbuf, rank_right, recvbuf=recvbuf, source=rank_left)
	# Right halo are refilled: data is sent to the left
	sendbuf = v[W_left:2*W_left]
	recvbuf = v[-W_right:]
	comm.Sendrecv(sendbuf, rank_left, recvbuf=recvbuf, source=rank_right)

def print_global(v_local):
	v_global = np.zeros(N_global)
	comm.Gather(v_local,v_global)
	if rank == 0:
		print(v_global)

# Main loop of conjugate gradient algorithm
has_converged = False
comm.Barrier()
t0 = time.monotonic_ns();
kmax = 2*N_global
for k in range(0,kmax):
	rr_local = np.vdot(r_local,r_local)
	comm.Allreduce(rr_local, rr_global, op=MPI.SUM)
	if rr_global <= tol**2 * bb_global:
		has_converged = True
		break
	if k == 0:
		beta = 0.0
	else:
		beta = rr_global / rr_global_old
	rr_global_old = rr_global.copy()
	p[0:] = r + beta*p
	v[0] = (2*p[0]-p[1])/(h*h)
	v[1:-1] = np.convolve(p,stencil,'valid')
	v[-1] = (-p[-2]+2*p[-1])/(h*h)
	v += sigma_x * p
	if W == 1:
		halo_exchange(v)
	elif (k+1) % W == 0:
		halo_exchange(r)
		halo_exchange(p)
		halo_exchange(v)
	pv_local = np.vdot(p_local,v_local)
	comm.Allreduce(pv_local, pv_global, op=MPI.SUM)
	alpha = rr_global / pv_global
	u[0:] = u + alpha*p
	r[0:] = r - alpha*v
comm.Barrier()
t1 = time.monotonic_ns();

# Append results to file
if rank == 0:
	results = open(filename,"a")
	print(f"Test with nprocesses = {nprocesses}, N_global = {N_global}, tol = {tol}, and W = {W}", file=results)
	if has_converged:
		print(f"Convergence reached after {k} iterations", file=results)
	else:
		print(f"Convergence not reached despite {kmax} iterations", file=results)
	dt = (t1-t0)
	performance = dt / (k * N_local)
	print(f"Elapsed time (main loop): {dt/1e9:.3f} s", file=results)
	print(f"Time per iteration per unknown: {performance:.3f} ns", file=results)

# Comparison with exact solution
err_local = u_local - u_exact(x_local)
err_Linf_local = np.max(np.abs(err_local))
err_Linf_global = np.zeros(1)
comm.Allreduce(err_Linf_local, err_Linf_global, op=MPI.MAX)
if rank == 0:
	print(f"Error in Linf norm: {float(err_Linf_global):.4e}\n", file=results)
