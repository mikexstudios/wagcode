#!/usr/bin/env python
'''
output_to_list.py
-----------------
Takes lowest scores (lowest energy structure) and outputs them in python list code
so that we can easily copy and paste into our structure generation code.
'''
__version__ = '0.1.0'
__date__ = '01 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import os #for path.isfile
import sqlite3
import math #For convert_bin_string_to_list
import create_twists

#Arguments
output_file = 'pretty_output_same_adj.txt'
max_horizontal_spots = 6 #This allows us to convert the long string into an array of strings.

eto_molecule_placements = [
        [[[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 0], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [0, [1,5,'z',180], [1,5,'z',180]], [1, 0, 1]],
        [[0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], 0, [1,5,'z',180]], [1, 1, 0]],
        [[1, 0, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [0, [1,5,'z',180], [1,5,'z',180]]],
        [[[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 0], [0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 0]],
        [[1, 1, 1], [[1,5,'z',180], 0, [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], 0], [1, 0, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]]],
        [[1, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], 0], [1, 0, 1], [[1,5,'z',180], [1,5,'z',180], 0]],
        [[1, 1, 0], [0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 0], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]]],
        [[0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], 0, [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], 0], [1, 1, 1]],
        [[1, 1, 0], [0, [1,5,'z',180], [1,5,'z',180]], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], 0], [1, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]]],
        [[[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [0, 1, 1], [[1,5,'z',180], 0, [1,5,'z',180]], [0, 1, 1], [[1,5,'z',180], [1,5,'z',180], [1,5,'z',180]], [1, 1, 1]],
    ]


def convert_bin_string_to_list(bin_string):
	global max_horizontal_spots
	
	max_iter = len(bin_string)/float(max_horizontal_spots)
	max_iter = int(math.ceil(max_iter)) #We want to round up so that our loop goes through the full string
	bin_list= []
	bin_string = list(bin_string) #We put each character in its own list element
	bin_string = map(int, bin_string) #Convert each element to int
	
	#Note for this method, it doesn't necessarily return a rectangular 2D list.
	for i in range(max_iter):
		bin_list.append(bin_string[0:max_horizontal_spots])
		bin_string = bin_string[max_horizontal_spots:] #Rest of the list
	
	return bin_list

def transpose_list(lists):
   if not lists: return []
   return map(lambda *row: list(row), *lists)

def main():
	global output_file
	global eto_molecule_placements

	f = file(output_file, 'w')
	
	for surf in eto_molecule_placements:
		#Uncomment if want twisted EtOH:
		#twisted_rep = create_twists.create_twists( \
		#	convert_bin_string_to_list(row['config']) \
		#	)
		#Comment out below since we want 6 in horizontal
		#twisted_rep = transpose_list(twisted_rep)
		#Now go in and do string replaces for -1 entries:
		#twisted_rep = str(twisted_rep)
		#twisted_rep = twisted_rep.replace('-1', "[1,5,'z',180]")
		#f.write(twisted_rep+", \n")
		
		#Replace all the twists with -1
		for row_index, row in enumerate(surf):
			for spot_index, spot in enumerate(row):
				if type(spot) == type([]):
					surf[row_index][spot_index]=-1
		
		surf = transpose_list(surf)

		#f.write(str(each_num_mol)+" EtOH: \n")
		for row in surf:
			for each_spot in row:
				if each_spot == -1:
					each_spot = 2 #Do this for now so that ASCII output can be all aligned
				f.write(str(each_spot))
			f.write("\n")
		f.write("\n")		
		
		#Uncomment if want non-twisted EtOH:
		#f.write(str(convert_bin_string_to_list(row['config']))+", \n")

	#f.write("]\n")
	f.close()

if __name__ == '__main__':
	main()
