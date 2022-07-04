import numpy as np
from mpi4py import MPI

# get communicator information
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# buffered sends prevent a deadlock here
if rank == 0:
	v = rank * np.ones(10)
	w = np.empty(10)
	comm.Bsend(v, 1)
	comm.Recv(w, 1)
	print(f"Process #{rank} has received {w}")
elif rank == 1:
	v = rank * np.ones(10)
	w = np.empty(10)
	comm.Bsend(v, 0)
	comm.Recv(w, 0)
	print(f"Process #{rank} has received {w}")
else:
	pass

comm.Barrier()

# synchronous mode causes a deadlock, instead
if rank == 0:
	v = rank * np.ones(10)
	w = np.empty(10)
	comm.Ssend(v, 1)
	comm.Recv(w, 1)
	print(f"Process #{rank} has received {w}")
elif rank == 1:
	v = rank * np.ones(10)
	w = np.empty(10)
	comm.Ssend(v, 0)
	comm.Recv(w, 0)
	print(f"Process #{rank} has received {w}")
else:
	pass
