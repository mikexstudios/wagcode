#!/bin/bash

for ((i=0; i <= 18; i++)); do
	each_etoh="$(printf 'etoh%02d' "$i")"
	#ln -s etoh_generic.auto $each_cmd
	#reax_automator ${each_etoh}.auto | tee ${each_etoh}.log &
	rm -rf ${each_etoh}
	rm ${each_etoh}.log
done
