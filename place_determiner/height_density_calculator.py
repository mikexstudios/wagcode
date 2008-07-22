#!/usr/bin/env python
'''
height_density_calculator.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '21 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

def shrink_height_by(number_of_liquid_molecules, number_of_surface_molecules,
		molecule_density, initial_cell_dimensions, surface_molecule_volume,
		surface_block_height):
	
	empty_height = initial_cell_dimensions[2] - surface_block_height
	#Find how much we need to shrink the z-height. Since python can't do
	#symbolic math out of the box (sympy looks promising), I did the symbolic
	#manipulation in Mathematica (see Caltech\Junior\Winter Term\Research
	#\week 03\etoh1_vchz.nb) and just used the resulting equation here 
	#(Angstrom):
	shrink_height_by = empty_height - \
		(number_of_liquid_molecules + molecule_density * surface_molecule_volume * number_of_surface_molecules) \
		/ (molecule_density * initial_cell_dimensions[0] * initial_cell_dimensions[1])

	return shrink_height_by

def main():
	#Arguments
	number_of_liquid_molecules = 54
	number_of_surface_molecules = 1
	molecule_density = 0.010313936489926729 #(EtOH) Molecules/Angstrom
	#initial_cell_height = 50 #Angstrom
	initial_cell_dimensions = (19.49070, 17.75400, 50.0) #Angstrom
	surface_molecule_volume = 76.9205 #Volume correction factor for placing molecule on surface. Angstrom
	surface_block_height = 16.0 #Angstrom. Assume that (x, y) dim. are the same.

	etoh_shrink_height_by = shrink_height_by(number_of_liquid_molecules, 
		number_of_surface_molecules, molecule_density, initial_cell_dimensions,
		surface_molecule_volume, surface_block_height)
	#So our final height is:
	print etoh_shrink_height_by
	print initial_cell_dimensions[2] - etoh_shrink_height_by


if __name__ == '__main__':
	main()
