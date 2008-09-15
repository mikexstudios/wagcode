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
    
    grouped_reactions = Grouped_Reactions_Wrapper()
    grouped_reactions.load(grprxns_file)
    print 'Grouped reaction file loaded: '+grprxns_file

    for each_grouped_reaction in grouped_reactions:
        molecule_numbers = get_all_unique_molecule_numbers(each_grouped_reaction)
        iterations = get_all_iterations(each_grouped_reaction)
        print molecule_numbers
        print iterations
        exit()


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
