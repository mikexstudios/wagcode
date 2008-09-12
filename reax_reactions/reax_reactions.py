#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
reax_reactions.py
-----------------
The purpose of this script is to analyze ReaxFF's fort.7 file to determine what
reactions have occured. These reactions will then be isolated so that the user
can view it in molden.

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
#import shutil
#import time #For sleep
#import math
#import re #For regex
from XYZ import XYZ #XYZ class
from reax.connection_table import Connection_Table
from reax.molecule_helper import Molecule_Helper

#Since we want to use /usr/bin/env to invoke python, we can't pass the -u flag
#to the interpreter in order to get unbuffered output. Nor do we want to rely on
#the environment variable PYTHONUNBUFFERED. Therefore, the only solution is to
#reopen stdout as write mode with 0 as the buffer:
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) 

#Arguments. Set some defaults before the control file in case the user does not
#define them.
suppress_molecule_rearrangment = False
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: reax_reactions [controlfile]'
    sys.exit(0)

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
    print 'Structure file loaded successfully: '+structure_file
    
    #Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
    connection_table = Connection_Table()
    connection_table.load(connection_table_file)
    print 'Connection table file loaded successfully: '+connection_table_file

    #The molecule helper class provides methods for working with both the XYZ
    #and connection table classes.
    molecule_helper = Molecule_Helper()
    molecule_helper.simulation_atoms_class = simulation_atoms
    molecule_helper.connection_table_class = connection_table
    molecule_helper.bondorder_cutoff = bondorder_cutoff

    #Open output file for writing:
    rxns_f = file(rxns_output_file, 'w')
    
    #Pretty/Instructional Output Stuff:
    rxns_f.write('#(NOTE: The molecule numbers are printed in parentheses. '+\
                 'ie. (3). The full table of molecules will be written to '+ 
                 'a binary file.)'+"\n\n")
    
    print 'Finding reactions',

    #Loop through all iterations. We are doing a do...while type loop here:
    connection_table_current = connection_table.next()
    for connection_table_next in connection_table:
        #We say that these are the reactions for the current iteration (and not
        #'from previous iteration to this iteration' just for simplicity.
        rxns_f.write('Reaction(s) for iteration: '+str(connection_table.iteration)+"\n")
        rxns_f.write('-------------------------------------------'+"\n\n")

        #Diff the two sets of molecules based on change in bond order. Figure out
        #which atoms have bond orders that were originally below the BO cutoff and
        #are now equal to or above the BO cutoff. This gives the atoms that have
        #changed connectivity.
        changed_atoms_entries = get_atoms_that_have_connection_changes(connection_table_current,
                            connection_table_next, bondorder_cutoff)
        #Then take these atoms that have changed, and get the molecule that
        #corresponds to it. First, let's transform the output we get into just a
        #list of changed atoms. Our approach is to put all the atoms into a list.
        #Then convert it into a set since that automatically eliminates all duplicate
        #elements.
        just_changed_atoms = []
        for each_changed_atom_entry in changed_atoms_entries:
            just_changed_atoms.append(each_changed_atom_entry[0])
            just_changed_atoms.append(each_changed_atom_entry[1])
        changed_atom_numbers = set(just_changed_atoms)

        #We want to connect reactants to products. See my notebook vol 2, p99 for
        #more explanation.
        #1. Get molecule from changed atoms. First, from reactants:
        reactant_molecules = []
        connection_table.rows = connection_table_current
        for each_changed_atom_number in changed_atom_numbers:
             reactant_molecules.append(
                 molecule_helper.get_molecule_for_atom(each_changed_atom_number)
             )
        #From products:
        product_molecules = []
        connection_table.rows = connection_table_next
        for each_changed_atom_number in changed_atom_numbers:
             product_molecules.append(
                 molecule_helper.get_molecule_for_atom(each_changed_atom_number)
             )
        #Now get rid of exact duplicates:
        reactant_molecules = remove_molecule_duplicates(reactant_molecules)
        product_molecules = remove_molecule_duplicates(product_molecules)
        
        #2. Now we relate the reactants and molecules with each other by finding 
        #   common atoms between them.
        reactants_to_products_mapping = group_reactants_and_products(
                                            reactant_molecules,
                                            product_molecules
                                        )

        #Suppress molecule rearrangement if needed. We define molecule rearragement
        #as when molecules on both sides of a reaction are the same!
        if suppress_molecule_rearrangment == True:
            new_reactants_to_products_mapping = []
            for each_mapping in reactants_to_products_mapping:
                if each_mapping['reactants'] != each_mapping['products']:
                    new_reactants_to_products_mapping.append(each_mapping)
            reactants_to_products_mapping = new_reactants_to_products_mapping

        #Output chemical formulas. This is a helper function for map:
        def molecule_to_chemical_formula_wrapper(molecule):
            '''
            Allows us to pass extra args when using map.
            '''
            return molecule_helper.molecule_to_chemical_formula(
                molecule, True
            )
        for each_reaction in reactants_to_products_mapping:
            #Get chemical formula. We include the molecule number next to each
            #formula:
            reactant_formulas = map(molecule_to_chemical_formula_wrapper,
                                    each_reaction['reactants'])
            product_formulas = map(molecule_to_chemical_formula_wrapper,
                                   each_reaction['products'])

            #List to string:
            reactant_formulas = ' + '.join(reactant_formulas)
            product_formulas = ' + '.join(product_formulas)
            rxns_f.write(reactant_formulas+' -> '+product_formulas+"\n\n")
    
        #Alright, let's move on to the next iteration,
        connection_table_current = connection_table_next
        #Give some indication of progress:
        print '.',
        rxns_f.write("\n")
    
    rxns_f.close()
    print
    print 'Successfully found reactions for every i to i+1 iteration: '+\
            rxns_output_file
    
    #Now that we generated all the reactions for i and i+1, let's output the
    #molecule dictionary as a pickled file.
    molecule_helper.save_molecule_list(molecules_output_file)
    print 'Successfully saved molecule list in binary format: '+molecules_output_file

def group_reactants_and_products(reactant_molecules, product_molecules):
    '''
    Given a list of reactant_molecules and product_molecules, determines the
    common atoms between both and creates a list of mappings that link reactants
    to products.

    Sample return:
    [{'reactants': [h_molecule, oh_molecule], 'products': [h2o_molecule]}, 
     {... similar ...}, etc.]
    '''
    #1. Take each reactant and find products that share similar atoms.
    #We link reactants to products using a list of dictionaries:
    reactants_to_products_mapping = []
    for each_reactant_molecule in reactant_molecules:
        reactants_to_products_mapping.append(
            {'reactants': [each_reactant_molecule],
             'products': []}
        )
        for each_product_molecule in product_molecules:
            if do_molecules_share_similar_atoms(
                each_reactant_molecule, each_product_molecule) == True:
                #Add to our mapping
                reactants_to_products_mapping[-1]['products'].append(
                    each_product_molecule
                )
    
    #2. Now group the products together. From step #1, we know that we correctly
    #   created the right side of the chemical reaction formula.
    new_reactants_to_products_mapping = []
    for i1, each_reactants_to_products_mapping in \
        enumerate(reactants_to_products_mapping):
        if each_reactants_to_products_mapping == None:
            continue
        for i2, each_reactants_to_products_mapping2 in \
            enumerate(reactants_to_products_mapping):
            if each_reactants_to_products_mapping2 == None:
                continue
            if i1 == i2: #Skip comparing to itself
                continue
            #If there is more than one product, we need to compare to each one.
            product_comparison_break = False #helps us break out of two 'for' loops
            for each_product in each_reactants_to_products_mapping['products']:
                if product_comparison_break == True:
                    break
                for each_product2 in each_reactants_to_products_mapping2['products']:
                    if each_product == each_product2: 
                        #As long as we have one match, we'll combine both
                        #reactions. There should be no exact duplicates in the
                        #reactants side (meaning that the atom numbers are the
                        #same) since we eliminated duplicates previously.
                        each_reactants_to_products_mapping['reactants'].extend(
                            each_reactants_to_products_mapping2['reactants']
                        )
                        #Also, the products side that has more products will be
                        #the dominant one.
                        #ie. OH vs H + OH. H + OH will dominate since it includes
                        #    OH.
                        if len(each_reactants_to_products_mapping2['products']) > \
                           len(each_reactants_to_products_mapping['products']):
                            each_reactants_to_products_mapping['products'] = \
                               each_reactants_to_products_mapping2['products']
                        #"Zero" out the entry that we just combined so that we don't
                        #have to process it again:
                        reactants_to_products_mapping[i2] = None
                        #Break out of this comparison:
                        product_comparison_break = True
                        break
        new_reactants_to_products_mapping.append(each_reactants_to_products_mapping)
    #reactants_to_products_mapping = new_reactants_to_products_mapping 
    return new_reactants_to_products_mapping

def do_molecules_share_similar_atoms(molecule1, molecule2):
    '''
    Given two molecules (a dictionary with atom numbers as keys and atom labels
    as values), returns True if the two molecules share at least one atom.
    Returns False if the two molecules do not share any atoms.
    '''
    for molecule1_atom_number in molecule1.keys():
        for molecule2_atom_number in molecule2.keys():
            if molecule1_atom_number == molecule2_atom_number:
                return True
    return False


def remove_molecule_duplicates(molecule_list):
    '''
    Given a list of molecules (each element is a dictionary with atom numbers as
    keys and atom label as values), removes duplicates from that list.
    '''
    #Since we are removing things, we won't want to mess with the original list.
    molecule_list_copy = molecule_list[:]
    new_molecule_list = []
    for each_i, each_molecule in enumerate(molecule_list_copy):
        if each_molecule == None:
            continue
        #Match this against all the other molecules
        for other_i, other_molecule in enumerate(molecule_list_copy):
            if each_molecule == None:
                continue
            if each_i == other_i:
                continue #This is the same molecule, so we skip.
            #We do a dictionary comparsion, if all the keys and values are the
            #same, then this is True:
            if each_molecule == other_molecule:
                molecule_list_copy[other_i] = None
        #Add this molecule to the new list. Copies won't be added since the
        #copies are None, which are skipped.
        new_molecule_list.append(each_molecule)
    return new_molecule_list

def get_atoms_that_have_connection_changes(connection_table_a, \
    connection_table_b, bondorder_cutoff):
    '''
    Given two connection tables (given as lists, not the class) and a
    bondorder_cutoff, returns a tuple of (atom number 1, atom number 2,
    difference in bond order) where the atoms all have bond formation or
    breakage defined by the bondorder_cutoff.

    For example, if we have a bondorder_cutoff of 0.6, then an H to O connection
    that originally was 0.3 and then changes to 0.65 would be defined as a bond
    formed (a positive difference in bond order). Whereas a bond order of 0.3
    that changes to 0.55 does not count as a bond formation.
    
    Sample return:
    [(3, 5, 0.23), (5, 4, 0.03), (183, 187, 0.81)]
    '''
    #Helper function:
    def remove_connection_duplicates(in_connection_changes):
        '''
        Given a list of connection changes, returns list without duplicates.

        A duplicate is defined as:
        1. Connection numbers are flipped (ie. instead of 2 to 3, it's 3 to 2).
        2. The change in bond order field is *exactly* the same.

        So (247, 254, -0.050000000000000044) and (254, 247,
        -0.050000000000000044) would be a duplicate. whereas (1, 2, 0.5) and (2,
        1, -0.5) is not.
        '''
        new_connection_changes = []
        #We create a copy since we need to zero out some elements
        in_connection_changes_copy = in_connection_changes[:]
        for each_connection_change in in_connection_changes_copy:
            #Check for zero'ed out elements:
            if each_connection_change == None:
                continue
            #Compare this to all the other entries:
            for i, each_connection_change2 in enumerate(in_connection_changes_copy):
                #Check for zero'ed out elements:
                if each_connection_change2 == None:
                    continue
                if each_connection_change[0] == each_connection_change2[1] and \
                   each_connection_change[1] == each_connection_change2[0] and \
                   each_connection_change[2] == each_connection_change2[2]:
                    in_connection_changes_copy[i] = None
                    break 
            new_connection_changes.append(each_connection_change)
        return new_connection_changes

    #We assume both connection tables have equal lengths and have the same
    #correspondence between each index. Then our algorithm is to go through each
    #atom and compare the bond order change.
    connection_changes = []
    #Each row in the connection table starts with the atom we are looking at
    #followed by the atoms it is connected to. So current_atom_number is the
    #number of the atom that we are looking at.
    for current_atom_number, connection_list_a in enumerate(connection_table_a):
        #Skip the first row since that was set to None
        if connection_list_a == None:
            continue
        #Get the same for b:
        connection_list_b = connection_table_b[current_atom_number]
        #Discard the first and last elements of connection_list since the first
        #element is the atom type (defined by ffield file) and the last element
        #is the molecule number.
        connection_list_a = connection_list_a[1:-1][0]
        connection_list_b = connection_list_b[1:-1][0]
        #print connection_list_b
        for connection_index, connection_a in enumerate(connection_list_a):
            connection_b = connection_list_b[connection_index]
            connection_a_atom_number, connection_a_bondorder = connection_a
            connection_b_atom_number, connection_b_bondorder = connection_b
            #Make sure the connection to the atom_numbers are the same. If not,
            #that means we formed a new bond and broken an old one.  But, note
            #that we still need to check and see if the bond order of forming a
            #new bond and breaking the old one meets are criteria. We are
            #assuming for now that the connection order won't suddently
            #rearrange itself while still keeping the same connections.
            #ie. 2, 3, 4, 5 -> 3, 5, 4, 2
            #Also, the bond order change in this case will just be the bond
            #order.
            if connection_a_atom_number != connection_b_atom_number:
                #Check to see if if the connections have just shifted around.
                found_same_connection_atom = False
                for temp_connection_b in connection_list_b:
                    temp_connection_b_atom_number = temp_connection_b[0]
                    if connection_a_atom_number == temp_connection_b_atom_number:
                        #So we found a match. This means that the connection
                        #numbers were just shifted around. Let's set this as our
                        #connection_b
                        connection_b_atom_number, connection_b_bondorder \
                            = temp_connection_b
                        found_same_connection_atom = True
                        break #out of this for loop
                
                if found_same_connection_atom == False:
                    #Check to see if the bond broken meets our BO cutoff criteria:
                    if connection_a_bondorder >= bondorder_cutoff:
                        #Add an entry for bond broken:
                        connection_changes.append((current_atom_number,
                            connection_a_atom_number, -1*connection_a_bondorder))
                    #Check to see if the bond formed meets our BO cutoff criteria:
                    if connection_b_bondorder >= bondorder_cutoff:
                        connection_changes.append((current_atom_number, 
                            connection_b_atom_number, connection_b_bondorder))
                    #This is for the next atom in the connection list. We want
                    #to skip the rest of the code below.
                    continue 
             
            #The connection is still the same. But let's check the bond
            #order to see if we formed or broken a connection. First, check
            #for bond broken:
            #NOTE: A little code redundancy here, but I think this makes things
            #      more readable.
            if connection_a_bondorder >= bondorder_cutoff and \
                connection_b_bondorder < bondorder_cutoff:
                connection_changes.append((current_atom_number, 
                    connection_a_atom_number, (connection_b_bondorder -
                                               connection_a_bondorder)))
            #Check for bond formed:
            elif connection_a_bondorder < bondorder_cutoff and \
                connection_b_bondorder >= bondorder_cutoff:
                connection_changes.append((current_atom_number, 
                    connection_a_atom_number, (connection_b_bondorder -
                                               connection_a_bondorder)))
            #Bond order changed, but no bond formed or broken:
            else:
                #Do nothing:
                pass
    
    #Now get rid of duplicates. Since atoms are connected to each other, we have
    #cases where if the bond order changes from below the cutoff to above the
    #cutoff or vice versa, we'll have two entries. The easiest way to get rid of
    #duplicates is to loop through the array (N^2 runtime) and check for
    #sameness. This isn't the most efficient way, but it separates the code
    #better. We're assuming that this array isn't that large so the extra cost of
    #runtime isn't a huge deal.
    #ie. (247, 254, -0.050000000000000044) and (254, 247, -0.050000000000000044)
    connection_changes = remove_connection_duplicates(connection_changes)

    return connection_changes     

def tests():
    #Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
    connection_table = Connection_Table()
    connection_table.load(connection_table_file)
    connection_table.next()
    connection_table_current = connection_table.rows[:]
    connection_table_next = connection_table.next() #We don't need to make copy here.
   
    #get_atoms_that_have_connection_changes tests:
    #print get_atoms_that_have_connection_changes(connection_table_current,
    #                                             connection_table_next,
    #                                             bondorder_cutoff)

    #Test list duplication removal:
    assert remove_molecule_duplicates(
        [{1: 'H', 2: 'H', 3: 'O'}, {13: 'Ti', 8: 'O', 10: 'O'}, 
         {1: 'H', 2: 'H', 3: 'O'}, {1: 'H', 2: 'H', 3: 'O', 4: 'O'}]) == \
        [{1: 'H', 2: 'H', 3: 'O'}, {13: 'Ti', 8: 'O', 10: 'O'}, 
         {1: 'H', 2: 'H', 3: 'O', 4: 'O'}]
    
    assert do_molecules_share_similar_atoms(
        {1: 'H', 2: 'H', 3: 'O'}, {13: 'Ti', 8: 'O', 10: 'O'}
    ) == False
    assert do_molecules_share_similar_atoms(
        {1: 'H', 2: 'H', 3: 'O'}, {1: 'H', 3: 'O', 2: 'H'}
    ) == True 
       
      

    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
