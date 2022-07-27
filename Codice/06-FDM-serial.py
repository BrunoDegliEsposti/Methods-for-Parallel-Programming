import os
os.environ['OMP_NUM_THREADS'] = '1'
import time
import numpy as np
from numpy import pi

# Define problem -u_xx + sigma(x)*u = f
xL = 0
xR = 1
N = 40000
h = (xR-xL)/(N+1)
sigma = lambda x: 1/(1+x*x)
f = lambda x: (pi*pi + 1/(1+x*x)) * np.sin(pi*x)
u_exact = lambda x: np.sin(pi*x)
uL = u_exact(xL)
uR = u_exact(xR)

# Initialize variables
x_bc = np.linspace(xL,xR,N+2)
x = x_bc[1:-1]
slope = (uR-uL)/(xR-xL)
u = slope*(x-xL)+uL
b = f(x)
b[0] += uL/(h*h)
b[-1] += uR/(h*h)
bb = np.vdot(b,b)
r = np.zeros(N)
stencil = np.array([-1/(h*h), 2/(h*h), -1/(h*h)])
sigma_x = sigma(x)
r = f(x)
p = r.copy()
v = np.zeros(p.shape)

# Main loop of conjugate gradient algorithm
kmax = 2*N
tol = 1e-12
has_converged = False
t0 = time.monotonic_ns();
for k in range(0,kmax):
	rr = np.vdot(r,r)
	if rr <= tol**2 * bb:
		has_converged = True
		break
	if k == 0:
		beta = 0.0
	else:
		beta = rr / rr_old
	rr_old = rr
	p = r + beta*p
	v[0] = (2*p[0]-p[1])/(h*h)
	v[1:-1] = np.convolve(p,stencil,'valid')
	v[-1] = (-p[-2]+2*p[-1])/(h*h)
	v += sigma_x * p
	alpha = rr / np.vdot(p,v)
	u += alpha*p
	r -= alpha*v
t1 = time.monotonic_ns();
if has_converged:
	print(f"Convergence reached after {k} iterations")
else:
	print(f"Convergence not reached despite {kmax} iterations")
dt = (t1-t0)
performance = dt / (k * N)
print(f"Elapsed time (main loop): {dt/1e9:.3f} s")
print(f"Time per iteration per unknown: {performance:.3f} ns")

# Comparison with exact solution
err = u - u_exact(x)
err_Linf = np.max(np.abs(err))
print(f"Error in Linf norm: {err_Linf:.4e}")
