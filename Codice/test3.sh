#!/usr/bin/env bash

counter=1
ntests=8

rm -f results-test-3.txt

for nprocesses in 1 2 4
do
	for W in 64 512
	do
		printf "Running test %d/%d...\n" $counter $ntests
		mpirun -H A660-Ubuntu:$nprocesses python3 07-FDM-parallel.py 160000 1e-12 $W results-test-3.txt
		let counter=counter+1
		sleep 5
	done
done

for W in 64 512
do
	printf "Running test %d/%d...\n" $counter $ntests
	mpirun -H A660-Ubuntu:4,N56VZ-Ubuntu:4 python3 07-FDM-parallel.py 160000 1e-12 $W results-test-3.txt
	let counter=counter+1
	sleep 5
done
