#!/usr/bin/env python
'''
reax/molecule_helper.py
-----------------
A class to encapsulate some helper functions that relate to working with
molecules constructed from ReaxFF output files (such as the connection table).

The reason why we use a class is because many of these helper functions require
access to the atoms file, connections file, and other settings (like bond order
cutoff). So that we don't have functions that *must* take each of these as
arguments, thus bloating up the arguments and making it less user friendly, we
wrap a class around the functions and set these arguments as class variables.

$Id:$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
import sys #for exit
#import re

class Molecule_Helper:
    #Define some class variables:
    simulation_atoms = None
    connection_table = None

    bondorder_cutoff = 0 #used by get_molecule_for_atom(...)

    def __init__(self):
        pass

    def get_molecule_for_atom(atom_number, molecule_dict=None):
        '''
        Given some atom number, will return the molecule in which that atom is part
        of.
    
        The second argument is for internal use only (used in recursion). The return
        format is a dictionary with the atom number as the keys and the atom label
        as the value. 
    
        Example return:
        {1: 'H', 2: 'O', 3: 'H'}
        '''
    	#We have to set molecule_label to default as None instead of [] because in python,
    	#default parameter values can be modified inside the function and remain modified.
    	#See: http://docs.python.org/ref/function.html. Using None is a way of getting around
    	#that.
    	if molecule_dict is None:
    		molecule_dict = {}
    		#Add current atom to the dictionary
    		molecule_dict[atom_number] = self.simulation_atoms.rows[atom_number-1] #-1 corrects for XYZ array
    
    	#We look up all the connections to this atom. Then recursively build up the rest of
    	#the molecule.
    	atom_connections = self.connection_table.rows[atom_number][1] #selecting only connections
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
    		if connection_num != 0 and connection_bondorder > self.bondorder_cutoff:
    			#Check to see if entry already exists in molecule_dict. If so, then we
    			#do nothing. Can also use .has_key() method.
    			try:
    				molecule_dict[connection_num]
    				pass #Do nothing
    			except KeyError:
    				#We can not add this connection to our molecule_dict. But first, let's check
    				#the bond order to make sure that it is a significant bond.
    				#Minus 1 on connection_num to correct for XYZ array
    				molecule_dict[connection_num] = self.simulation_atoms.rows[connection_num-1]
    				#molecule_label.append(self.simulation_atoms.rows[connection_num][0])
    				#Recursively find if this connection atom is connected to anything else.
    				molecule_dict = get_molecule_for_atom(connection_num, molecule_dict)
    	
    	return molecule_dict

    def get_atom_label_list_from_molecule(in_parts):
        '''
        Given a molecule (in the form of a dictionary returned from the function
        get_molecule_for_atom), returns the atom labels in the form of a list.
    
        Example return:
        ['H', 'O', 'H']
        '''
    	molecule_list= []
    	for atom_part in in_parts.values():
    		molecule_list.append(atom_part[0]) #Append just the atom string label
    	return molecule_list

def tests():
    molecule_helper = Molecule_Helper()



    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

