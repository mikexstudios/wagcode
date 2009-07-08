#!/bin/bash
# Purpose of this script is to setup some files for ReaxFF molfra
# analysis program I wrote. It must be run in the same directory
# as the simulation files.
# by Michael Huynh (mikeh@caltech.edu)
# $Id$

mkdir molfra_analysis
cd molfra_analysis
ln -s ../molfra.out .

cp ~/scripts/reax_molfra/control .
