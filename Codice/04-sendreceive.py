import numpy as np
from mpi4py import MPI

# get communicator information
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocesses = comm.Get_size()

# another way to prevent a deadlock is to use sendrecv()
# comm.Sendrecv(sendbuf, dest, sendtag=0, recvbuf=None, source=ANY_SOURCE, recvtag=ANY_TAG, status=None)
v = rank * np.ones(10)
w = np.empty(10)
prev_rank = (rank-1) % nprocesses
next_rank = (rank+1) % nprocesses
comm.Sendrecv(v, next_rank, recvbuf=w, source=prev_rank)
print(f"Process #{rank} has received {w}")
