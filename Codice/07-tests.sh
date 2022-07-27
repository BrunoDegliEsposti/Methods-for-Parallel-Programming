#!/usr/bin/env bash

counter=1

rm -f 07-results.txt

for nprocesses in 1 2 4
do
	for N_global in 20000 40000 80000 160000
	do
		for W in 1 8 128 1024
		do
			printf "Running test %d...\n" $counter
			mpirun -n $nprocesses python3 07-FDM-parallel.py $N_global 1e-12 $W
			let counter=counter+1
			sleep 5
		done
	done
done
