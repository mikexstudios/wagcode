#!/bin/bash
# Converts .geo files to .xyz files using Adri's d2x2 program.
# Usage: geo_to_xyz [file.geo]
#
# DEPENDENCIES: d2x2 (from Adri)
#
# by Michael Huynh (mikeh@caltech.edu, http://www.mikexstudios.com)

#Generate a random name for the temp directory in case we already have a
#directory called temp
TEMP_DIR="temp_${RANDOM}"
FILENAME_NOEXT=${1%%.*} #See: http://list.mail.virginia.edu/pipermail/uvalug/Week-of-Mon-20050418/000079.html

mkdir $TEMP_DIR
cp $1 $TEMP_DIR/fort.54
cd $TEMP_DIR
d2x2
if [ -e fort.55 ]
then
	echo "XYZ file successfully generated from GEO!"
	cp fort.55 ../${FILENAME_NOEXT}.xyz
	cd ..
	rm -rf $TEMP_DIR
	echo "${FILENAME_NOEXT}.xyz created!"
else
	echo "ERROR: fort.55 not found!"
fi
