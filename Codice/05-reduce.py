import numpy as np
from mpi4py import MPI

# get communicator information
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocesses = comm.Get_size()

# sum the rank of all processes
# comm.Reduce(sendbuf, recvbuf, op=SUM, root=0)
v = rank * np.ones(1)
v_sum = np.zeros(1)
comm.Reduce(v, v_sum, op=MPI.SUM)
if rank == 0:
	print(f"Sum of all ranks: {v_sum}")
