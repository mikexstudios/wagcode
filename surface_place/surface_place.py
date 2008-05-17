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
import copy #Create copy of objects

#Arguments
surface_xyz_file = '0etoh.xyz'
place_xyz_file = 'placed_eto_orientation.xyz' #The molecule we want to place on the surface
output_xyz_file = 'placed.xyz'
#Define the longer axis as the axis where more molecules can be placed
#(see the molecule placement array). We also define the upper left atom as the one
#closer to (0, 0):
upper_left_surface_atom  = Struct(x =  1.69501, y =  0.71964, z = 31.50097) #In Angstroms
lower_right_surface_atom = Struct(x = 14.68505, y = 15.51403, z = 31.51654) 
placement_z_distance_from_surface = 1.8141 #The distance of our 'to place' molecule from the surface. 
molecule_placement = [      #Use 1 to indicate placement of the molecule, 0 is vacant spot.
		[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1]
		]

#Calculated Arguments
spacing_of_target_atoms = Struct()
surface = XYZ()
place_molecule = XYZ()

def main():
	global output_xyz_file
	global surface

	initialize()
	place_surface_molecules()

	#Now save the surface and any placed molecules
	surface.export(output_xyz_file)
	print 'Surface placed file created: ' + output_xyz_file


def initialize():
	global upper_left_surface_atom, lower_right_surface_atom
	global molecule_placement
	global spacing_of_target_atoms
	global place_xyz_file, place_molecule
	global surface_xyz_file, surface
	
	number_of_target_atoms = Struct() 
	number_of_target_atoms.x = len(molecule_placement[0])
	number_of_target_atoms.y = len(molecule_placement)
	#print number_of_target_atoms.x
	#print number_of_target_atoms.y
	
	spacing_of_target_atoms.x = abs(upper_left_surface_atom.x-lower_right_surface_atom.x)/(number_of_target_atoms.x-1) #-1 because counting atom connections
	spacing_of_target_atoms.y = abs(upper_left_surface_atom.y-lower_right_surface_atom.y)/(number_of_target_atoms.y-1) #-1 because counting atom connections
	
	#print spacing_of_target_atoms.x
	#print spacing_of_target_atoms.y
	
	#Load our surface and place molecule
	surface.load(surface_xyz_file)	
	place_molecule.load(place_xyz_file)
	place_molecule.normalize_coordinates() #Make the molecule start from (0,0,0)
	#Make the molecule start from the upper left position
	place_molecule.translate(upper_left_surface_atom.x, upper_left_surface_atom.y, upper_left_surface_atom.z)
	
	#Testing rotation:
	place_molecule.rotate_wrt_atom(5, 'z', 90.0)

def place_surface_molecules():
	global molecule_placement
	global spacing_of_target_atoms
	global surface, place_molecule
	global placement_z_distance_from_surface

	for row_index, row in enumerate(molecule_placement):
		for spot_index, each_spot in enumerate(row):
			if each_spot == 1:
				print 'Placing molecule at: ('+str(spot_index)+', '+str(row_index)+')'
				#We have a spot marked for placement. Let's place the molecule
				#Note: We *must* use deepcopy since the XYZ class uses lists which
				#      are references.
				temp_place_molecule = copy.deepcopy(place_molecule)
				temp_place_molecule.translate( #In initialize, we already translated to upper left position.
						spot_index * spacing_of_target_atoms.x,
						row_index * spacing_of_target_atoms.y,
						placement_z_distance_from_surface
						)
				print spot_index * spacing_of_target_atoms.x
				print row_index * spacing_of_target_atoms.y
				print placement_z_distance_from_surface
				surface.add(temp_place_molecule)
				del temp_place_molecule #Don't need it since we added to the surface


if __name__ == '__main__':
    main()
