#!/bin/bash
# Purpose of this script is to setup some files for ReaxFF Reaction
# analysis programs I wrote. It must be run in the same directory
# as the simulation files.
# by Michael Huynh (mikeh@caltech.edu)
# $Id:$

convert_fort98
mkdir reactions_analysis
cd reactions_analysis
ln -s ../fort.7 .
ln -s ../xmolout .
ln -s ../fort.98.xyz .

cp ~/scripts/reax_reactions/control rxns.control
cp ~/scripts/group_reactions/control grprxns.control
cp ~/scripts/isolate_grouped_reactions/control isolate.control
