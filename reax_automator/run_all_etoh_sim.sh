#!/bin/bash

for ((i=0; i <= 18; i++)); do
	each_etoh="$(printf 'etoh%02d' "$i")"
	#ln -s etoh_generic.auto $each_cmd
	reax_automator ${each_etoh}.auto | tee ${each_etoh}.log &
	#By sleeping, we keep all of the simulations from bunching up
	#against each other.
	random_time=`expr $RANDOM % 10`
	echo "Sleeping for ${random_time}"
	sleep $random_time
done
