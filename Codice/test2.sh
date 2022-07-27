#!/usr/bin/env bash

counter=1
ntests=16

rm -f results-test-2.txt

for nprocesses in 1 2 4
do
	for W in 1 8 128 1024
	do
		printf "Running test %d/%d...\n" $counter $ntests
		mpirun -H A660-Ubuntu -np $nprocesses python3 07-FDM-parallel.py 40000 1e-12 $W results-test-2.txt
		let counter=counter+1
		sleep 5
	done
done

for W in 1 8 128 1024
do
	printf "Running test %d/%d...\n" $counter $ntests
	mpirun -H A660-Ubuntu,N56VZ-Ubuntu -np 8 python3 07-FDM-parallel.py 40000 1e-12 $W results-test-2.txt
	let counter=counter+1
	sleep 5
done
