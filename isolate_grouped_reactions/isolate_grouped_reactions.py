#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
isolate_grouped_reactions.py
-----------------
The purpose of this script is to allow the user to select a grouped reaction
(from the .grprxns output file generated from group_reactions.py) and generate
an appended XYZ file which can be visualized in programs such as Molden.

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
from grouped_reactions_wrapper import Grouped_Reactions_Wrapper
from reax.molecule_helper import Molecule_Helper
#import time

#Since we want to use /usr/bin/env to invoke python, we can't pass the -u flag
#to the interpreter in order to get unbuffered output. Nor do we want to rely on
#the environment variable PYTHONUNBUFFERED. Therefore, the only solution is to
#reopen stdout as write mode with 0 as the buffer:
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) 

#Arguments. Set some defaults before the control file in case the user does not
#define them.
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: group_reactions [controlfile]'
    sys.exit(0)

#Source the control file:
try:
    execfile(control_file)
except IOError: 
    print 'Error: '+control_file+' does not exist!'
    sys.exit(1)
print 'Read control file successfully: '+control_file


def main():
    #There are two things we want:
    #1. List of all molecule numbers
    #2. List of all iterations (for simplicity, we'll just take the first and
    #   last iterations so that we know the range that we want to operate over.)
    global grouped_reactions 
    grouped_reactions = Grouped_Reactions_Wrapper()
    grouped_reactions.load(grprxns_file)
    print 'Grouped reaction file loaded: '+grprxns_file
    
    global molecule_helper
    molecule_helper = Molecule_Helper()
    molecule_helper.load_molecule_list(molecules_file)
   
    for each_grouped_reaction in grouped_reactions:
        #Check if our argument is an integer. If so, then we'll just process
        #only that grouped reaction number.
        if type(isolate_grouped_reaction_number) == type(1):
            if grouped_reactions.grouped_reaction_number != \
               isolate_grouped_reaction_number:
                continue #We'll skip these
    
        print 'Processing grouped reaction: '+str(grouped_reactions.grouped_reaction_number),
        
        includeall_isolate_grouped_reaction(each_grouped_reaction)
        #exact_isolate_grouped_reaction(each_grouped_reaction)
        
        print

def exact_isolate_grouped_reaction(each_grouped_reaction):
    '''
    Given a grouped reaction, will isolate the atoms based on the 'exact'
    critera (only specific iterations that are defined will be processed and
    only the molecules defined for that iteration will be processed).

    NOTE: This function depends on grouped_reactions and molecule_helper being
          global.
    '''
    iterations = get_all_iterations(each_grouped_reaction)
    iterations = set(iterations)

    #Now we go through all the iterations in the appended XYZ file (xmolout)
    xmolout = XYZ()
    xmolout.load(appendedxyz_file)
    
    new_xyz = XYZ() #We will use this to write our isolated XYZ structure.

    for each_xyz in xmolout:
        print '.',
        
        #Check if we are at one of the iterations in our grouped reaction list.
        #If not, then we skip:
        if xmolout.iteration not in iterations:
            continue #skip this iteration
       
        #Otherwise, process this iteration, keeping ONLY the molecules defined
        #in this iteration.

        new_xyz.rows = []
        #Compare each atom to our atom numbers.
        for i, atom in enumerate(each_xyz):
            each_xyz_atom_number = i+1 #Since atom numbers start at 1 not 0.
            if each_xyz_atom_number in atom_numbers:
                new_xyz.rows.append(atom)
        #Now append this new xyz to our output file:
        output_xyz_filename = appendedxyz_output_file.replace(
                                '[grouped_reaction_number]',
                                str(grouped_reactions.grouped_reaction_number)
                              )
        new_xyz.export(output_xyz_filename, append=True)

def includeall_isolate_grouped_reaction(each_grouped_reaction):
    '''
    Given a grouped reaction, will isolate the atoms based on the 'includeall'
    critera (all molecules in this grouped reaction over the entire iteration
    range will be kept).

    NOTE: This function depends on grouped_reactions and molecule_helper being
          global.
    '''
    molecule_numbers = get_all_unique_molecule_numbers(each_grouped_reaction)
    iterations = get_all_iterations(each_grouped_reaction)
    
    #We will find the range of iterations we need to operate over:
    start_iteration = iterations[0]
    end_iteration = iterations[-1]
    
    #Get all the atom numbers in the molecules involved in this reaction
    #pathway.
    atom_numbers = get_all_unique_atoms_for_molecule_numbers(
                    molecule_helper, molecule_numbers
                   )
    atom_numbers = set(atom_numbers) #Make into set so we can do quick lookups
    
    #Now we go through all the iterations in the appended XYZ file (xmolout)
    #and isolate these molecules. We do this by getting all the atoms in the
    #molecules we want to isolate. Then simply keep those atoms and delete
    #all other ones.
    xmolout = XYZ()
    xmolout.load(appendedxyz_file)
    
    new_xyz = XYZ() #We will use this to write our isolated XYZ structure.

    for each_xyz in xmolout:
        print '.',
        
        #Check if we are in the range of iterations that are grouped reactions
        #are defined for:
        if xmolout.iteration < start_iteration or \
           xmolout.iteration > end_iteration:
            continue #skip this iteration

        new_xyz.rows = []
        #Compare each atom to our atom numbers.
        for i, atom in enumerate(each_xyz):
            each_xyz_atom_number = i+1 #Since atom numbers start at 1 not 0.
            if each_xyz_atom_number in atom_numbers:
                new_xyz.rows.append(atom)
        #Now append this new xyz to our output file:
        output_xyz_filename = appendedxyz_output_file.replace(
                                '[grouped_reaction_number]',
                                str(grouped_reactions.grouped_reaction_number)
                              )
        new_xyz.export(output_xyz_filename, append=True)

def get_all_unique_atoms_for_molecule_numbers(molecule_helper, molecule_numbers):
    '''
    Given the molecule_helper object and a list of molecule numbers, will return
    a unique list of atoms in those molecules.

    NOTE: We assume that molecule_helper has already been loaded with the
          molecule list.
    '''
    unique_atoms = set([])
    for each_molecule_number in molecule_numbers:
        unique_atoms.update(
            molecule_helper.get_atom_numbers_from_molecule(
                molecule_helper.get_molecule_from_number(each_molecule_number)
            )
        )
    return list(unique_atoms)

def get_all_unique_molecule_numbers(grouped_reaction):
    '''
    Given a grouped reaction (list of tuples which first element iteration,
    second element a reaction dictionary), will return all the unique molecule
    numbers in the whole grouped reaction.

    Sample return:
    [4, 35, 654, 23, 64]
    '''
    molecule_numbers = set([]) #Sets are unique
    for each_reaction in grouped_reaction:
        reaction_dict = each_reaction[1]
        for reactants_or_products in reaction_dict.values():
            #There are cases where we have more than one molecule on any side of
            #the reaction equation:
            for molecule_entry in reactants_or_products:
                #Add molecule number to set:
                molecule_numbers.add(int(molecule_entry[0]))
    return list(molecule_numbers)

def get_all_iterations(grouped_reaction):
    '''
    Given a grouped reaction (list of tuples which first element iteration,
    second element a reaction dictionary), will return all the iterations
    involved in the grouped reaction (sorted in ascending order).

    Sample return:
    [0, 15, 30, 45, 60]
    '''
    iterations = set([]) #Sets are unique
    for each_reaction in grouped_reaction:
        iterations.add(int(each_reaction[0]))
    return sorted(list(iterations))

def tests():
    rxn01 = [(15, {'reactants': [(1, 'H'), (2, 'O')], 'products': [(3, 'H2O')]})]
    assert get_all_unique_molecule_numbers(rxn01) == [1, 2, 3]
    assert get_all_iterations(rxn01) == [15]


    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
