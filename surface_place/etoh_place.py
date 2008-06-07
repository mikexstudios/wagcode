#!/usr/bin/env python
'''
etoh_place.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '07 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
from surface_place import *
from Struct import * #Just a small class allowing us to create objects on the fly
from XYZ import *


def main():
	#Molecule placement: Use 1 to indicate placement of the molecule, 0 is vacant spot. If you want to
	# rotate the molecule, enter a list that takes the arguments: 
	# [1, (int) atom to rotate wrt, (str) axis, (float) degrees]
	# ie. To rotate EtOH molecule about its O molecule along the z axis 180 degrees:
	#     [1, 5, 'z', 180]
	eto_molecule_placement = [      
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1]
			]
	
	eto_place = Surface_place()
	eto_place.set_filenames('0etoh.xyz', 'placed_eto_orientation.xyz', 'eto_placed.xyz')
	eto_place.define_surface_sites(
			Struct(x =  1.69501, y =  0.71964, z = 31.50097), 
			Struct(x = 14.68505, y = 15.51403, z = 31.51654), 
			1.8141
			)
	eto_place.define_molecule_placement(eto_molecule_placement)

	eto_place.initialize()
	eto_place.place()

	#Now save the surface and any placed molecules
	eto_place.surface.export(eto_place.output_xyz_file)
	print 'Surface placed file created: ' + eto_place.output_xyz_file

	#Now we place the H's that correspond to the EtO:
	h_atom_placement= [      
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1],
			[1, 1, 1]
			]
	h_place = Surface_place()
	h_place.set_filenames('eto_placed.xyz', 'placed_h_orientation.xyz', 'placed.xyz')
	h_place.define_surface_sites(
		Struct(x =  4.96824, y =  0.80220, z = 32.54942), 
		Struct(x = 17.89190, y = 15.57038, z = 32.54436),      
		1.00325
		)

	h_place.define_molecule_placement(h_atom_placement)

	h_place.initialize()
	h_place.place()
	
	#Now save the surface and any placed molecules
	h_place.surface.export(h_place.output_xyz_file)
	print 'Surface placed file created: ' + h_place.output_xyz_file


if __name__ == '__main__':
    main()
