from mpi4py import MPI

# get communicator information
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocesses = comm.Get_size()

# print a message from every process
msg = f"Hello from process {rank+1}/{nprocesses}"
msg += f" running on {MPI.Get_processor_name()}"
print(msg)
