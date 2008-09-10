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

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
import sys #for exit
#import re
import hashlib #only for python 2.5+
import pickle #convert object to string for eventual hashing

class Molecule_Helper:
    #Define some class variables:
    simulation_atoms_class = None
    connection_table_class = None

    bondorder_cutoff = 0.30 #used by get_molecule_for_atom(...)

    #Used by molecule number methods:
    molecule_list = [] #Keeps track of the molecules we assign numbers too.

    def __init__(self):
        pass
    
    def get_all_molecules(self):
        '''
        Returns all molecules (a list of molecule dictionaries) present in the
        connection table.
        '''
        #The way we approach this problem is that we loop once through
        #simulation atoms. For each atom, we grab the molecule that contains that
        #atom. Then we zero out the atoms in that molecule (by setting those
        #atoms to None) in the simulation atoms. That way, we don't need to
        #reduplicate work.

        #Helper function
        def remove_molecule_from_atoms(molecule, atoms_list):
            '''
            Given a molecule dictionary input (this is what we get from the
            get_molecule_for_atom function), removes (by setting to None) the
            corresponding atoms in the atoms list (ie. simulation_atoms).
            '''
            for atom_number in molecule.keys():
                i = atom_number-1 #correction since atoms_list starts at 0 index
                atoms_list[i] = None
            return atoms_list #technically don't need this since atoms_list is ref

        #Make copy so we don't mess up original when we set entries to None:
        simulation_atoms_copy = self.simulation_atoms_class.rows[:]
        all_molecules = [] #Holds all the returned molecule dictionaries
        for i, atom in enumerate(simulation_atoms_copy):
            #Check to see if the atom has been cleared:
            if atom == None:
                continue #Go to next atom!
            atom_number = i + 1 #correction since atom numbers start at 1
            molecule_for_atom = self.get_molecule_for_atom(atom_number)
            all_molecules.append(molecule_for_atom)
            #Now clear out these atoms in our simulation atoms copy:
            simulation_atoms_copy = remove_molecule_from_atoms(
                molecule_for_atom, simulation_atoms_copy
            )
        return all_molecules 


    def get_molecule_for_atom(self, atom_number, molecule_dict=None):
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
    		molecule_dict[atom_number] = self.simulation_atoms_class.rows[atom_number-1] #-1 corrects for XYZ array
    
    	#We look up all the connections to this atom. Then recursively build up the rest of
    	#the molecule.
    	atom_connections = self.connection_table_class.rows[atom_number][1] #selecting only connections
    	#molecule_label = []
    	for connection in atom_connections:
    		#Determine the atom type of each of the connections. Note that connection is a tuple.
    		#The first element is the atom number connected to. The second element is the bond
    		#order.
    		connection_num, connection_bondorder = connection
    		
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
    				molecule_dict[connection_num] = self.simulation_atoms_class.rows[connection_num-1]
    				#molecule_label.append(self.simulation_atoms.rows[connection_num][0])
    				#Recursively find if this connection atom is connected to anything else.
    				molecule_dict = self.get_molecule_for_atom(connection_num, molecule_dict)
    	
    	return molecule_dict

    def get_atom_label_list_from_molecule(self, in_parts):
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

    def atom_label_list_to_formula(self, atom_list):
        '''
        Given an atom list (ie. ['H', 'O', 'H']), groups it into a string
        formula like: H2O. This allows for more consistency when comparing
        molecules.
        '''
        #We sort it all into a dictionary keep track of the atom count.
        atoms_dict = {}
        for atom in atom_list:
            try:
                atoms_dict[atom] += 1
            except KeyError:
                #Means that this is our first encounter with such atom
                atoms_dict[atom] = 1
        #Now sort by alphabetical order:
        atom_labels = atoms_dict.keys()
        atom_labels.sort()
        #Generate molecular formula:
        molecular_formula = ''
        for atom_label in atom_labels:
            molecular_formula += atom_label
            #If there is only one atom, don't print out the 1 next to it.
            #(ie. We want H instead of H1)
            if atoms_dict[atom_label] > 1:
                molecular_formula += str(atoms_dict[atom_label])
        return molecular_formula

    def molecule_to_chemical_formula(self, molecule_atom_list,
                                     include_molecule_number=False):
        '''
        Given a molecule (in dictionary format), returns the chemical formula.
        This removes any ability to uniquely identify the molecule. But it's
        easier to read.

        This method is just a wrapper around get_atom_label_list_from_molecule 
        and atom_label_list_to_formula since I find myself using both functions
        together a lot.

        Sample return:
        'H2O'
        '''
    	chemical_formula = self.atom_label_list_to_formula(
            self.get_atom_label_list_from_molecule(
                molecule_atom_list
            )
        )
        if include_molecule_number == True:
            chemical_formula += \
                ' ('+str(self.get_molecule_number(molecule_atom_list))+')'
        return chemical_formula


    def molecule_list_to_frequency_dict(self, in_molecule_list):
        '''
        Given a molecule list (in dictionary format, probably returned from the
        get_all_molecules(...) method), returns a dictionary of molecule formula
        and frequency.

        Sample return:
        {'H2O': 5, 'H2': 2}
        '''
        molecule_dict = {}
        for each_molecule in in_molecule_list:
            molecule_formula = self.atom_label_list_to_formula(
                self.get_atom_label_list_from_molecule(each_molecule)
            )
            try:
                molecule_dict[molecule_formula] += 1
            except KeyError:
                #Means that this is our first encounter with this molecule:
                molecule_dict[molecule_formula] = 1
        return molecule_dict

    def give_molecule_a_number(self, molecule):
        '''
        Given a molecule (in dictionary format), adds this molecule to our
        internal list of molecules and returns a number that is unique to this
        molecule.
        '''
        self.molecule_list.append(molecule)

        return len(self.molecule_list)-1 #since lists start at index 0

    def get_molecule_number(self, molecule):
        '''
        Given a molecule (in dictionary format), returns the unique number of
        this molecule. If the molecule didn't already exist in the dictionary,
        then it will be automatically added and the molecule number returned.

        NOTE: Currently this method searches through the whole list. As the list
        grows, we scale like O(n). But keep in mind that we also need to do an
        O(n) comparison of the molecule dictionaries too. In worse case, we'll
        have O(n^2) runtime. This all can be optimized by using dictionary and
        hashes, see p100 of vol 2 of my notebook.
        '''
        for i, each_molecule in enumerate(self.molecule_list):
            if molecule == each_molecule:
                return i
        #Molecule was not found. So we'll add it:
        return self.give_molecule_a_number(molecule)

def tests():
    #Currently assume some relative path stuff. This is apt to change once we
    #make this into a module.
    sys.path.insert(0, "..") #Make this the first thing since we want to override
    from XYZ import XYZ #XYZ class
    from reax_connection_table import Connection_Table
   
    #Test files location:
    structure_file = 'tests/a10a_ph7.xyz'
    connection_table_file = 'tests/a10a_ph7.connect'

    #Read in XYZ file. Store all the coordinates.
    simulation_atoms = XYZ()
    simulation_atoms.load(structure_file) #simulation_atoms.rows contains the data
    print 'Structure file loaded successfully: '+structure_file
    
    #Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
    connection_table = Connection_Table()
    connection_table.load(connection_table_file)
    connection_table.next()
    print 'Connection table file loaded successfully: '+connection_table_file

    molecule_helper = Molecule_Helper()
    molecule_helper.simulation_atoms_class = simulation_atoms
    molecule_helper.connection_table_class = connection_table
    molecule_helper.bondorder_cutoff = 0.6

    assert molecule_helper.atom_label_list_to_formula(['H', 'O', 'H']) == 'H2O'
    #print molecule_helper.atom_label_list_to_formula(['H', 'O', 'H'])
    assert molecule_helper.atom_label_list_to_formula(['H']) == 'H'
    assert molecule_helper.atom_label_list_to_formula(['H', 'H', 'Ti', 'O', 'Ti', 'P']) == 'H2OPTi2'

    all_molecules = molecule_helper.get_all_molecules()
    #We compare this to molfra.out file generated by ReaxFF with bond order
    #cutoff of 0.6
    assert molecule_helper.molecule_list_to_frequency_dict(all_molecules) == \
        {'HO20Ti10': 1, 'H2O81Ti40': 1, 'H3O41Ti20': 1, 'H2O': 149, 'O20Ti10': 6, 'HO': 1, 'H2O40Ti20': 1, 'HO21Ti10': 3}
    
    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

