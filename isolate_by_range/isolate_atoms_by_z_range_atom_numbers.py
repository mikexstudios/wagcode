#!/usr/bin/env python
'''
isolate_atoms_by_z_range_atom_numbers.py
------------------------
Given an XYZ file and a z range, isolates those atoms.

This version adds the output of atom numbers. Used these numbers
to get charges from fort.56 file.
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import sys
#import re
#import math
from XYZ import *

#Parameters
structure_file = 'test.xyz'
output_file = 'test_atom_numbers.txt'
surface_z_min = 31.0    #Defines the starting z coordinates for the surface
surface_z_max = 33.0    #Defiles the ending z coordinates for the surface

def get_atom_numbers_by_z_range(xyz_rows, z_min, z_max):
    #Format of XYZ file is:
    # [atom] [x] [y] [z]
    atom_numbers = []
    for row_i, row in enumerate(xyz_rows):
        if row[3] >= z_min and row[3] <= z_max:
            atom_numbers.append(row_i+1) #+1 correction since atom # starts at 1
    return atom_numbers

def main():
    structure = XYZ()
    structure.load(structure_file)
    
    atom_numbers = get_atom_numbers_by_z_range(
        structure.rows, surface_z_min, surface_z_max
    )

    f = file(output_file, 'w')
    for atom_number in atom_numbers:
        f.write(str(atom_number)+"\n")
    f.close()


if __name__ == '__main__':
	main()
