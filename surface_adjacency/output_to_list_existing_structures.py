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
output_file = 'output_to_list_existing_structures.txt'
max_horizontal_spots = 6 #This allows us to convert the long string into an array of strings.

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
	global placed_mol_binary_rep
	
	f = file(output_file, 'w')
	f.write("eto_molecule_placements = [\n")
	#Make a table of the best score in each category:
	for each_config in placed_mol_binary_rep:
		#Uncomment if want twisted EtOH:
		#twisted_rep = create_twists.create_twists( \
		#	convert_bin_string_to_list(row['config']) \
		#	)
		#twisted_rep = transpose_list(twisted_rep)
		##Now go in and do string replaces for -1 entries:
		#twisted_rep = str(twisted_rep)
		#twisted_rep = twisted_rep.replace('-1', "[1,5,'z',180]")
		#f.write(twisted_rep+", \n")
		
		#Uncomment if want non-twisted EtOH:
		f.write(str(transpose_list(convert_bin_string_to_list(each_config)))+", \n")

	f.write("]\n")
	f.close()
	
if __name__ == '__main__':
	main()
