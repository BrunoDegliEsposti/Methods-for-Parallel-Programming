import numpy as np
from mpi4py import MPI

# get communicator information
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocesses = comm.Get_size()

# make sure that nprocesses is 2
if nprocesses != 2 and rank == 0:
	print("Error: number of processes must be 2")
	comm.Abort()
comm.Barrier()

# send a small buffer from rank 0 to rank 1
# comm.Send(buffer, destination_rank, tag=0)
# comm.Recv(buffer, source=ANY_SOURCE, tag=ANY_TAG, status=None)
if rank == 0:
	v = np.array([-1.0,2.0])
	comm.Send(v, 1)
else:
	v = np.zeros(10, dtype=np.float64)
	print(v)
	comm.Recv(v[0:2], source=0)
	print(v)
