#!/bin/bash

for ((i=0; i <= 18; i++)); do
	each_cmd="$(printf 'etoh%02d.auto\n' "$i")"
	ln -s etoh_generic.auto $each_cmd
done
