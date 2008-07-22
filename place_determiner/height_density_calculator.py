#!/usr/bin/env python
'''
place_determiner.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '21 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import sys #For arguments and exit (in older python versions)
#import os #For file exist check and splitext and path stuff
#import shutil
#import time #For sleep
#import re #For regex

#Arguments
number_of_liquid_molecules = 54
number_of_surface_molecules = 1
molecule_density = 0.010313936489926729 #(EtOH) Molecules/Angstrom
#initial_cell_height = 50 #Angstrom
initial_cell_dimensions = (19.49070, 17.75400, 50.0) #Angstrom
surface_molecule_volume = 76.9205 #Volume correction factor for placing molecule on surface. Angstrom
surface_block_height = 16.0 #Angstrom. Assume that (x, y) dim. are the same.

def main():
	global number_of_liquid_molecules, number_of_surface_molecules
	global molecule_density
	global initial_cell_dimensions, surface_molecule_volume
	
	empty_height = initial_cell_dimensions[2] - surface_block_height
	#Find how much we need to shrink the z-height. Since python can't do
	#symbolic math out of the box (sympy looks promising), I did the symbolic
	#manipulation in Mathematica (see Caltech\Junior\Winter Term\Research
	#\week 03\etoh1_vchz.nb) and just used the resulting equation here 
	#(Angstrom):
	shrink_height_by = empty_height - \
		(number_of_liquid_molecules + molecule_density * surface_molecule_volume * number_of_surface_molecules) \
		/ (molecule_density * initial_cell_dimensions[0] * initial_cell_dimensions[1])

	#So our final height is:
	print shrink_height_by
	print initial_cell_dimensions[2] - shrink_height_by


if __name__ == '__main__':
	main()
