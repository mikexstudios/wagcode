#!/usr/bin/env python
'''
surface_place.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '11 May 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
from Struct import * #Just a small class allowing us to create objects on the fly
from XYZ import *

#Arguments
surface_xyz_file = '0etoh.xyz'
to_place_xyz_file = 'ethanol.xyz'
#Define the longer axis as the axis where more molecules can be placed
#(see the molecule placement array):
upper_left_surface_atom =  Struct(x = 15.51403, y = 14.68505, z = 31.51654)
lower_right_surface_atom = Struct(x =  0.71964, y =  1.69501, z = 31.50097)
molecule_placement = [      #Use 1 to indicate placement of the molecule, 0 is vacant spot.
		[1, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0]
		];


#Calculated Arguments
number_of_target_atoms = Struct() #{'x': 6, 'y': 3} #Number of times target atom repeats along that axis.
spacing_of_target_atoms = Struct()
to_place_molecule = XYZ()

def main():
    initialize()
    print 'nothing'

def initialize():
	global upper_left_surface_atom, lower_right_surface_atom
	global molecule_placement
	global number_of_target_atoms, spacing_of_target_atoms
	global to_place_xyz_file, to_place_molecule
	
	number_of_target_atoms.x = len(molecule_placement[0])
	number_of_target_atoms.y = len(molecule_placement)
	#print number_of_target_atoms.x
	#print number_of_target_atoms.y
	
	spacing_of_target_atoms.x = abs(upper_left_surface_atom.x-lower_right_surface_atom.x)/(number_of_target_atoms.x-1) #-1 because counting atom connections
	spacing_of_target_atoms.y = abs(upper_left_surface_atom.y-lower_right_surface_atom.y)/(number_of_target_atoms.y-1) #-1 because counting atom connections
	
	#print spacing_of_target_atoms.x
	#print spacing_of_target_atoms.y

	to_place_molecule.load(to_place_xyz_file)	


if __name__ == '__main__':
    main()
