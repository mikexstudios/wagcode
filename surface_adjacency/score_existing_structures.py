#!/usr/bin/env python
'''
score_existing_structures.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '18 May 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import surface_adjacency

#Arguments
surface_adjacency.max_horizontal_spots = 6 #This allows us to convert the long string into an array of strings.
output_file = 'score_existing_structures.txt'

def main():
	
	#These are our representations from 1 to 18 EtOH on surface
	placed_mol_binary_rep = [
			'100000000000000000',
			'100000000000100000',
			'100000100000100000',
			'100010100000100000',
			'100010100010100000',
			'100010100010100010',
			'100010100010101010',
			'101010100010101010',
			'101010101010101010',
			'101011101010101010',
			'101011111010101010',
			'101011111010101110',
			'101011111011101110',
			'101011111011111110',
			'101111111011111110',
			'101111111011111111',
			'111111111011111111',
			'111111111111111111'
			]


	f = file(output_file, 'w')
	f.write("Best of each number of molecules:\n")
	f.write("# Mol \t Config \t Horiz. Adj. \t Vert. Adj. \t Score\n")
	f.write("----------------------------------------------------------------\n")

	#Now we go through each one and evaulate the adjacencies
	for each_bin_rep in placed_mol_binary_rep:
		#Convert to 2 array of our surface sites:
		each_surf_rep = surface_adjacency.convert_bin_string_to_list(each_bin_rep)
		num_mol = surface_adjacency.get_num_occupied_spots(each_surf_rep)
		adjacencies = surface_adjacency.evaluate_adjacencies(each_surf_rep)
		score = surface_adjacency.score_adjacencies(adjacencies[0], adjacencies[1])

		print str(num_mol)+"\t"+str(each_bin_rep)+"\t"+str(adjacencies[0])+\
				"\t"+str(adjacencies[1])+"\t"+str(score)
		f.write(str(num_mol)+"\t"+str(each_bin_rep)+"\t"+str(adjacencies[0])+
				"\t"+str(adjacencies[1])+"\t"+str(score)+"\n")
	
	f.close()

if __name__ == '__main__':
	main()
