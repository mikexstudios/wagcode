#!/usr/bin/env python
'''
reax_rdf.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '05 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
#import shutil
#import time #For sleep
import re #For regex
from XYZ import XYZ #XYZ class
from reax_connection_table import Connection_Table

#Arguments
control_file= sys.argv[1] #Settings for RDF

#Source the control file:
try:
	execfile(control_file)
except IOError: 
	print 'Error: '+control_file+' does not exist!'
	sys.exit(1)
print 'Read control file successfully: '+control_file

def main():
	#Read in XYZ file. Store all the coordinates.
	simulation_atoms = XYZ()
	simulation_atoms.load(structure_file) #simulation_atoms.rows contains the data
	
	#Pre-sort the atoms by atom type (into a dictionary). This way, we don't
	#have to loop through the whole file every time we calculate distances for
	#a given atom.
	simulation_atoms_dict = {}
	for atom_number, each_row in enumerate(simulation_atoms.rows):
		#Correction to the atom_number since it starts at 1 instead of 0:
		atom_number += 1
		
		#We want our new list to be in the format:
		#atom_number x y z
		temp_list = [atom_number] #Put it in a list first. For some reason, 
		temp_list.extend(each_row[1:]) #can't combine these two on same line.
		
		#Now save it:
		try:
			simulation_atoms_dict[each_row[0]].append(temp_list)
		except KeyError:
			#This means that the dictionary entry for this atom has not been
			#created yet. So we create it:
			simulation_atoms_dict[each_row[0]] = [temp_list] #New list
	
	#Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
	connect_table = Connection_Table()
	connect_table.load(connection_table_file)

	#Loop through each pair of atoms.
	for each_row in simulation_atoms.rows:
		if each_row[0] == from_atom:
			#Calculate interatomic distances. Use the minimum image convention here to
			#take care of any periodic conditions. We start by checking through all the
			#other atoms to see if they match our to_atom:
			for each_target_row in simulation_atoms.rows:
				if each_target_row[0] == to_atom:
					#Make sure this to_atom isn't part of the same molecule. We figure
					#this out by using the connection table:
					if connection_table.rows[each_row
						
						
				 

	#Normalize the histrogram by comparing to ideal gas.



def get_minimum_image_distance(in_coord):
	pass

if __name__ == '__main__':
	main()
