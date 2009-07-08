#!/usr/bin/env python
'''
isolate_atoms_by_z_range.py
------------------------
Given an XYZ file and a z range, isolates those atoms.
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
output_file = 'test_surface.xyz'
surface_z_min = 31.0    #Defines the starting z coordinates for the surface
surface_z_max = 33.0    #Defiles the ending z coordinates for the surface

def get_atoms_by_z_range(xyz_rows, z_min, z_max):
    #Format of XYZ file is:
    # [atom] [x] [y] [z]
    new_rows = []
    for row in xyz_rows:
        if row[3] >= z_min and row[3] <= z_max:
            new_rows.append(row)
    return new_rows

def main():
    structure = XYZ()
    structure.load(structure_file)
    
    structure.set_rows(
        get_atoms_by_z_range(structure.rows, surface_z_min, surface_z_max)
    )

    structure.export(output_file)



if __name__ == '__main__':
	main()
