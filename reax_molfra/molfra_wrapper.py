#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
molfra_wrapper.py
-----------------
Class that wraps around the molfra.out file and makes it an iterator.

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #for exit
import re

class Molfra_Wrapper:
    #Define some class variables:
    f = None #File handle for rxns file
    #num_mol_regex = re.compile('^\s+(\d+)\s+(\d+)\s+x\s+([a-zA-Z0-9]+)\s+[0-9\.]\s*');

    def __init__(self):
        pass
    
    def __iter__(self):
        '''We want this to be iterable.'''
        return self

    def load(self, input_file):
        self.f = file(input_file)
        self.reset()

    def reset(self):
        '''
        Resets the iterator back to the beginning.
        '''
        self.f.seek(0)
        self.f.next() #Discard first line, which is bond order cutoff line.

    def next(self):
        '''
        Loads the next iteration of reactions and returns it. 

        Returns a dictionary. The key is the molecule chemical formula, the
        value is the frequency.
        
        Sample return:
        {'O360Ti180': 1, 'H2O': 170}
        '''
        f = self.f #Just to simplify things
        mol_dict = {}
        
        #Find the first line of the reaction block. Sample line:
        #Iteration Freq. Molecular formula               Molecular mass
        begin_regex = re.compile(r'^Iteration Freq\.\s+Molecular formula\s+Molecular mass')
        begin_match = begin_regex.match(f.next())
        if begin_match:
            pass #Do nothing
        else:
            print 'ERROR: Beginning of molfra block could not be found!' 
            sys.exit(1)

        #Okay, now process all the molecule fragments
        #detect the end of this molfra block with total number of molecules line:
        #Total number of molecules:         171
        num_mol_regex = re.compile(r'^\s*Total number of molecules:\s+(\d+)\s*')

        for line in f:
            #Check for number of molecules:
            num_mol_match = num_mol_regex.match(line)
            if num_mol_match:
                self.total_number_molecules = int(num_mol_match.group(1))
                #Throw out next two lines
                f.next()
                f.next()
                break
            
            #A sample line is like:
            #      0   1 x  O360Ti180                          14378.0400
            #So we'll split by x first.
            split_by_x = line.split('x')
            iteration_frequency = split_by_x[0].split()
            self.iteration = int(iteration_frequency[0])
            frequency = int(iteration_frequency[1])
            molecule_formula_and_mass = split_by_x[1].split()
            molecule_formula = molecule_formula_and_mass[0]

            #Now add this to our dictionary:
            try:
                mol_dict[molecule_formula]
                print 'Weird, this molecule appeared again, which it should not: '+molecule_formula
            except KeyError:
                #This is the correct behavior:
                mol_dict[molecule_formula] = frequency

        return mol_dict

    def get_all_unique_molecule_formulas(self):
        '''
        Returns a list of all molecule formulas encountered in the molfra.out
        file.

        NOTE: This MUST be called either before using the iterator or after
        since we reset the iterator after calling this method!

        Sample return:
        ['H2O', 'H3O', 'OH']
        '''
        molecule_formulas = set([])
        for each_mol_dict in self:
            molecule_formulas.update(each_mol_dict.keys())
        self.reset() #Reset the iterator
        return list(molecule_formulas)

def tests():
    molfra = Molfra_Wrapper()
    molfra.load('molfra.out')
    
    print molfra.get_all_unique_molecule_formulas()

    print molfra.next()
    print molfra.iteration
    print molfra.total_number_molecules

    print molfra.next()
    print molfra.iteration
    print molfra.total_number_molecules
    
    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

