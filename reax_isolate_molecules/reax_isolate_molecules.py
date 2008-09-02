#!/usr/bin/env python
'''
reax_isolate_molecules.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '14 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
#import os #For file exist check and splitext and path stuff
#import shutil
#import time #For sleep
#import math
#import re #For regex
from XYZ import XYZ #XYZ class
from reax_connection_table import Connection_Table

#Arguments
#The isolate method can be either 'include' or 'exclude'. 'include' means that ONLY
#the target molecules will remain after isolation. 'exclude' means that NONE of the target
#molecules will remain after isolation.
isolate_method = 'exclude' 
#The isolate criteria can be either 'exact' or 'including'. 'exact' means that molecules
#containing exactly the specified atoms in target_molecules will be acted upon. 'including'
#means that molecules containing at least the specified atoms in target_molecules will be
#acted upon.
isolate_criteria = 'including' #Either: 'exact' or 'including'
#Target molecules are specified as a list of tuples.
target_molecules = [
		('H', 'O', 'H')
		]
#Bond cutoff. This is the lowest value in which we will consider the bond being a "real"
#bond. Any BO below this will be disregarded. The cutoff is useful in excluding hydrogen
#bonds from being processed when determining what the "molecule" is for a given atom.
bondorder_cutoff = 0.5

structure_file = 'test.xyz'
connection_table_file = 'fort.7'
output_xyz_file = 'test_out.xyz'

def tests():
	a = ['H', 'O', 'H']
	b = ['H', 'O', 'O', 'H']
	c = ['C', 'H', 'H', 'H']
	d = ['Cl']
	
	assert are_molecules_the_same(a, a[:]) == True
	assert are_molecules_the_same(a, a[:], 'including') == True
	assert are_molecules_the_same(a, b) == False
	assert are_molecules_the_same(b, a) == False
	assert are_molecules_the_same(a, b, 'including') == True
	assert are_molecules_the_same(b, a, 'including') == False
	assert are_molecules_the_same(b, c) == False
	assert are_molecules_the_same(b, c, 'including') == False
	assert are_molecules_the_same(c, b, 'including') == False
	assert are_molecules_the_same(a, d) == False
	assert are_molecules_the_same(a, d, 'including') == False
	
	Cl_ion_test = get_molecule_for_atom(548)
	print Cl_ion_test
	print molecule_parts_to_list(Cl_ion_test)
	print Cl_ion_test
	print are_molecules_the_same(a, molecule_parts_to_list(Cl_ion_test))

	print 'All tests completed successfully!'
	sys.exit(0)

def main():
	
	#Read in XYZ file. Store all the coordinates.
	global simulation_atoms, simulation_atoms_dict
	simulation_atoms = XYZ()
	simulation_atoms.load(structure_file) #simulation_atoms.rows contains the data
	simulation_atoms_dict = simulation_atoms.return_sorted_by_atoms_dict()
	#NOTE: Now we have two tables, simulation_atoms and simulation_atoms_dict

	#Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
	global connection_table #So that other functions can access this
	connection_table = Connection_Table()
	connection_table.load(connection_table_file)

	#Testing
	#tests()

	#Go through each of the target molecules and do isolation stuff:
	for target_molecule in target_molecules:
		#Select an atom to work with. We just select the first one. Used for the 'exclude'
		#case so that we don't have to check every single atom in simulation_atoms:
		an_atom = target_molecule[0] 
		#Loop through all the atoms matching the an_atom type:
		for atom_number, each_atom in enumerate(simulation_atoms.rows):
			#Correction to the atom_number since XYZ list starts at 0 but atom numbers
			#start at 1:
			atom_number += 1

			#Somewhat of a hack: Do a quick check here to see if this atom has been
			#nullified in the XYZ object. If so, we can just skip it since this atom
			#has been "deleted".
			if each_atom == None:
				continue #skip this atom since it has been deleted
			
			#If the isolate_method is 'include' then we have to check all atoms because
			#there are cases of single atoms and/or atoms not connected to the target
			#molecule atoms that we defined which we won't catch unless we check every 
			#atom. If the isolate method is 'exclude' then we just have to check atoms that
			#are connected to an atom in the defined target molecule.
			if isolate_method == 'exclude' and each_atom[0] != an_atom:
				#Skip this atom for now. If it's part of the target molecule, we'll
				#automatically come back to it later.
				continue
			
			#For the current atom, get the molecule that corresponds to it:
			molecule_parts = get_molecule_for_atom(atom_number)
			
			#Check this molecule against our isolation specification see if match exists:
			same_molecules_q = are_molecules_the_same( \
				list(target_molecule),
				molecule_parts_to_list(molecule_parts),
				isolate_criteria
				)

			#Get the molecule numbers so that we can feed it into the nullify atoms func.
			molecule_atom_numbers = molecule_parts.keys()
			#Now keep/remove depending on criteria:
			if isolate_method == 'include':
				if same_molecules_q != True:
					#print molecule_parts
					#The molecules are not the same so we need to delete it	
					nullify_atoms_in_XYZ(molecule_atom_numbers)
			elif isolate_method == 'exclude':
				if same_molecules_q == True:
					#This molecule is in the excluded list so we need to delete it
					nullify_atoms_in_XYZ(molecule_atom_numbers)
			else:
				print 'ERROR: isolate_method option invalid!'
				sys.exit(0)

	#Cool, we now ran through the whole XYZ file. Let's save the changed version:
	simulation_atoms.export(output_xyz_file)
	print 'Processed XYZ file exported: '+output_xyz_file

def nullify_atoms_in_XYZ(atom_numbers):
	'''
	By nullify, we just make that array entry a None object. We'll check for it later
	and rebuild the XYZ file without the None's later. The reason why we don't just delete
	is to keep the index to atom_number mapping consistent.
	'''
	global simulation_atoms

	for atom_number in atom_numbers:
		#-1 is correction for XYZ list since it starts at zero
		simulation_atoms.rows[atom_number-1] = None
		

def are_molecules_the_same(molecule_a, molecule_b, extra_criteria='exact'):
	molecule_a = molecule_a[:] #Copy so that we don't destroy the original list (it's referenced!)
	molecule_a_copy = molecule_a[:] #We remove stuff from the copy
	molecule_b = molecule_b[:]
	
	#Assume inputs are list of atoms
	for i_a, atom_a in enumerate(molecule_a):
		for i_b, atom_b in enumerate(molecule_b):
			if atom_a == atom_b:
				del molecule_b[i_b] #Remove atom
				#del molecule_a_copy[i_a] #Remove atom from a too so we know that match is success
				molecule_a_copy[i_a] = '' #Clear the molecule, but don't delete the index
				break #Don't keep on deleting atoms from b, let's move on to another A atom
	#Now remove all the ''s in molecule_a_copy
	molecule_a_copy = ''.join(molecule_a_copy)
	molecule_a_copy = list(molecule_a_copy) #split word into individual letters
	#Check for exact condition:
	if molecule_b == [] and molecule_a_copy == []:
		return True
	#If the match wasn't exact (which is by default), let's check if our extra criteria
	#is 'including'. If that's the case, we just need molecule_a to be an empty list:
	#NOTE: This is specific to the order in which the molecules are specified. ie. Is A
	#      included in B? Is B included in A?
	if extra_criteria == 'including':
		if molecule_a_copy == []: #We don't do: or molecule_b == [] here.
			return True
	#Molecules are not the same:
	return False

def molecule_parts_to_list(in_parts):
	molecule_list= []
	for atom_part in in_parts.values():
		molecule_list.append(atom_part[0]) #Append just the atom string label
	return molecule_list

def get_molecule_for_atom(atom_number, molecule_dict=None):
	global simulation_atoms, connection_table
	global bondorder_cutoff

	#We have to set molecule_label to default as None instead of [] because in python,
	#default parameter values can be modified inside the function and remain modified.
	#See: http://docs.python.org/ref/function.html. Using None is a way of getting around
	#that.
	if molecule_dict is None:
		molecule_dict = {}
		#Add current atom to the dictionary
		molecule_dict[atom_number] = simulation_atoms.rows[atom_number-1] #-1 corrects for XYZ array

	#We look up all the connections to this atom. Then recursively build up the rest of
	#the molecule.
	atom_connections = connection_table.rows[atom_number][1] #selecting only connections
	#molecule_label = []
	for connection in atom_connections:
		#Determine the atom type of each of the connections. Note that connection is a tuple.
		#The first element is the atom number connected to. The second element is the bond
		#order.
		connection_num, connection_bondorder = connection
		#if connection_bondorder > 0.2 and connection_bondorder < 0.6:
		#	print connection
		
		#0 means not connected to anything. We also want bonds that are greater than
		#our defined cutoff (this is to exclude atoms from being in a molecule just because
		#they are hydrogen bonding to it):
		if connection_num != 0 and connection_bondorder > bondorder_cutoff:
			#Check to see if entry already exists in molecule_dict. If so, then we
			#do nothing. Can also use .has_key() method.
			try:
				molecule_dict[connection_num]
				pass #Do nothing
			except KeyError:
				#We can not add this connection to our molecule_dict. But first, let's check
				#the bond order to make sure that it is a significant bond.
				#Minus 1 on connection_num to correct for XYZ array
				molecule_dict[connection_num] = simulation_atoms.rows[connection_num-1]
				#molecule_label.append(simulation_atoms.rows[connection_num][0])
				#Recursively find if this connection atom is connected to anything else.
				molecule_dict = get_molecule_for_atom(connection_num, molecule_dict)
	
	return molecule_dict

if __name__ == '__main__':
	main()
