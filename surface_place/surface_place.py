#!/usr/bin/env python
'''
surface_place.py
-----------------
07 June 2008 - Added rotation syntax. Changed into a class.
'''
__version__ = '0.2.0'
__date__ = '07 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
from Struct import * #Just a small class allowing us to create objects on the fly
from XYZ import *
import copy #Create copy of objects

class Surface_place:

	def __init__(self):
		pass
	
	def set_filenames(self, in_surface_file, in_place_file, in_output_file):
		self.surface_xyz_file = in_surface_file
		self.place_xyz_file = in_place_file #The molecule we want to place on the surface
		self.output_xyz_file = in_output_file
	
	def define_surface_sites(self, in_upper_left, in_lower_right, in_z_dist):
		self.upper_left_surface_atom = in_upper_left #In Angstroms
		self.lower_right_surface_atom = in_lower_right
		self.placement_z_distance_from_surface = in_z_dist

	def define_molecule_placement(self, in_placement_config):
		self.molecule_placement = in_placement_config
	
	def initialize(self):
		self.number_of_target_atoms = Struct() 
		self.number_of_target_atoms.x = len(self.molecule_placement[0])
		self.number_of_target_atoms.y = len(self.molecule_placement)
		
		self.spacing_of_target_atoms = Struct()
		self.spacing_of_target_atoms.x = abs(self.upper_left_surface_atom.x- \
			self.lower_right_surface_atom.x)/(self.number_of_target_atoms.x-1) #-1 because counting atom connections
		self.spacing_of_target_atoms.y = abs(self.upper_left_surface_atom.y- \
			self.lower_right_surface_atom.y)/(self.number_of_target_atoms.y-1) #-1 because counting atom connections
		
		#Load our surface and molecule placing position
		self.surface = XYZ()
		self.surface.load(self.surface_xyz_file)

		self.place_molecule = XYZ()
		self.place_molecule.load(self.place_xyz_file)
		self.place_molecule.normalize_coordinates() #Make the molecule start from (0,0,0)
		#Make the molecule start from the upper left position
		self.place_molecule.translate(self.upper_left_surface_atom.x, self.upper_left_surface_atom.y,  \
			self.upper_left_surface_atom.z)
		
	def place(self):
		for row_index, row in enumerate(self.molecule_placement):
			for spot_index, each_spot in enumerate(row):
				#We check for any list type first so that we can make modifications
				#before doing translation and placing.
				if each_spot != 0:
					temp_place_molecule = copy.deepcopy(self.place_molecule)

				if [].__class__ == type(each_spot): #If it is a list
					print 'Rotating molecule: '+str(each_spot[1])
					#Rotate the molecule
					temp_place_molecule.rotate_wrt_atom(each_spot[1], each_spot[2], each_spot[3]) 
					each_spot = each_spot[0] #Set equal to just an integer so we can translate it later
					
				#if type(1) == type(each_spot): #If integer
				if each_spot == 1:
					print 'Placing molecule at: ('+str(spot_index)+', '+str(row_index)+')'
					#We have a spot marked for placement. Let's place the molecule
					#Note: We *must* use deepcopy since the XYZ class uses lists which
					#      are references.
					temp_place_molecule.translate( #In initialize, we already translated to upper left position.
							spot_index * self.spacing_of_target_atoms.x,
							row_index * self.spacing_of_target_atoms.y,
							self.placement_z_distance_from_surface
							)
					#print spot_index * self.spacing_of_target_atoms.x
					#print row_index * self.spacing_of_target_atoms.y
					#print self.placement_z_distance_from_surface
					self.surface.add(temp_place_molecule)
					del temp_place_molecule #Don't need it since we added to the surface

def main():
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
	
	#Molecule placement: Use 1 to indicate placement of the molecule, 0 is vacant spot. If you want to
	# rotate the molecule, enter a list that takes the arguments: 
	# [1, (int) atom to rotate wrt, (str) axis, (float) degrees]
	# ie. To rotate EtOH molecule about its O molecule along the z axis 180 degrees:
	#     [1, 5, 'z', 180]
	molecule_placement = [      
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1]
			]
	
	ethanol_place = Surface_place()
	ethanol_place.set_filenames(surface_xyz_file, place_xyz_file, output_xyz_file)
	ethanol_place.define_surface_sites(upper_left_surface_atom, lower_right_surface_atom, placement_z_distance_from_surface)
	ethanol_place.define_molecule_placement(molecule_placement)

	ethanol_place.initialize()
	ethanol_place.place()

	#Now save the surface and any placed molecules
	ethanol_place.surface.export(output_xyz_file)
	print 'Surface placed file created: ' + output_xyz_file


if __name__ == '__main__':
    main()
