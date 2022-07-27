#!/usr/bin/env bash

counter=1
ntests=10

rm -f results-test-1.txt

for N in 5000 10000 20000 40000 80000
do
	printf "Running test %d/%d...\n" $counter $ntests
	python3 06-FDM-serial.py $N 1e-12 results-test-1.txt
	let counter=counter+1
	sleep 5
done

for N in 5000 10000 20000 40000 80000
do
	printf "Running test %d/%d...\n" $counter $ntests
	mpirun -H A660-Ubuntu -np 1 python3 07-FDM-parallel.py $N 1e-12 1 results-test-1.txt
	let counter=counter+1
	sleep 5
done
