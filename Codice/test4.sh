#!/usr/bin/env bash

counter=1
ntests=16

rm -f results-test-4.txt

for nprocesses in 1 2 4
do
	for W in 1 8 128 1024
	do
		printf "Running test %d/%d...\n" $counter $ntests
		let N_global=20000*nprocesses
		mpirun -H A660-Ubuntu:$nprocesses python3 07-FDM-parallel.py $N_global 1e-12 $W results-test-4.txt
		let counter=counter+1
		sleep 5
	done
done

for W in 1 8 128 1024
do
	printf "Running test %d/%d...\n" $counter $ntests
	let N_global=20000*8
	mpirun -H A660-Ubuntu:4,N56VZ-Ubuntu:4 python3 07-FDM-parallel.py $N_global 1e-12 $W results-test-4.txt
	let counter=counter+1
	sleep 5
done
