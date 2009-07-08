#!/bin/bash
#1. Removes the crystal lines from fort.98
#2. Converts fort.98 to the other xyz format with d2x2.
#3. Writes file to fort.98.xyz

mkdir temp
cp fort.98 temp/
cd temp/
echo "F file" > fort.54
tail +4 fort.98 >> fort.54
d2x2
cp fort.55 ../fort.98.xyz
cd ..
rm -rf temp/
