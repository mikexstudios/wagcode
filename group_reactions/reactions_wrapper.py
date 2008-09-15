#!/usr/bin/env python
'''
reactions_wrapper.py
-----------------
Class that makes the .rxns output file from reax_reactions an object
(specifically, an Iterator).

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
import sys #for exit
import re
#import pickle #convert object to string for eventual hashing

class Reactions_Wrapper:
    #Define some class variables:
    f = None #File handle for rxns file
    reactions_list = []
    iteration = 0

    def __init__(self):
        pass
    
    def __iter__(self):
        '''We want this to be iterable.'''
        return self
   
    def load(self, input_file):
        self.f = file(input_file)

        #Discard the first two informative lines
        self.f.next()
        self.f.next()

    def next(self):
        '''
        Loads the next iteration of reactions and returns it. 

        Returns a list of dictionaries. The dictionaries have keys 'reactants'
        and 'products'. The values are tuples with first element being molecule
        number, second element being molecule formula. Sample return:
        [{'reactants': [(1, 'H'), (2, 'O')], 'products': [(3, 'H2O')]},
         {'reactants': ..., 'products': ...}, 
         etc.]
        '''
        f = self.f #Just to simplify things

        #Process the iterations line. Sample line:
        #Reaction(s) for iteration: 15
        iteration_regex = re.compile(r'^Reaction\(s\) for iteration: (\d+)')
        iteration_match = iteration_regex.match(f.next())
        if iteration_match:
            self.iteration = int(iteration_match.group(1))
            #Skip the next line which is just the divider line:
            #-------------------------------------------------
            f.next()
        else:
            print 'ERROR: Iteration line could not be found!'
            sys.exit(1)

        #Okay, now process all the reactions within this iteration. We
        #detect the end of this iteration by two consecutive new lines.
        newline_counter = 0
        #NOTE: This reactants_to_products_mapping data structure is different
        #      than the one used in reax_reactions.
        reactants_to_products_mapping = []
        for line in f:
            #Check for new lines/blank lines. Two consecutive new lines
            #signify the end of the iteration.
            if line.strip() == '':
                newline_counter += 1
                if newline_counter >= 2:
                    #We are at the end of this iteration
                    break
                #Otherwise, go to the next line
                continue
            #If not a newline, reset the counter:
            newline_counter = 0

            #Now parse reaction lines into dictionary and append to list.
            reactants_to_products_mapping.append(
                parse_reaction_line(line)
            )
        
        return reactants_to_products_mapping

    def parse_reaction_line(self, line):
        '''
        Given a reaction string, ie. H (1) + OH (2) -> H2O (3), will return a
        dictionary of this reaction. The dictionary will have keys 'reactants'
        and 'products'. The values are lists of tuples with first element
        molecule number, the second element molecule formula.

        Sample return:
        {'reactants': [(1, 'H'), (2, 'OH')], 'products': [(3, 'H2O')]}
        '''
        split_by_arrow = line.split('->')
        reactions_side = split_by_arrow[0]
        products_side = split_by_arrow[1]

        reaction_molecules_with_num = reactions_side.split('+')
        product_molecules_with_num = products_side.split('+')

        #Parse the molecule number next to molecule chemical formula:
        reaction_molecules = []
        for each_mol_with_num in reaction_molecules_with_num:
            each_mol_with_num = each_mol_with_num.strip()
            #Add to our list as a tuple:
            parsed_molecule_formula_with_number = \
                self.parse_molecule_formula_with_number(each_mol_with_num)
            if parsed_molecule_formula_with_number != False:
                reaction_molecules.append(
                    parsed_molecule_formula_with_number
                )

        #Do the same with product molecules. 
        product_molecules = []
        for each_mol_with_num in product_molecules_with_num:
            each_mol_with_num = each_mol_with_num.strip()
            #Add to our list as a tuple:
            parsed_molecule_formula_with_number = \
                self.parse_molecule_formula_with_number(each_mol_with_num)
            if parsed_molecule_formula_with_number != False:
                product_molecules.append(
                    parsed_molecule_formula_with_number
                )
        
        return {'reactants': reaction_molecules, 'products': product_molecules}

    def parse_molecule_formula_with_number(self, in_formula_with_number):
        '''
        Given a molecular formula with the molecule number in parentheses (ie.
        H2O (1)), returns a tuple of the (molecule number, molecule formula).
        '''
        #The \w in regex means alphanumeric and _
        #NOTE: This regex is fairly specific because we are relying on the fact
        #      that reax_reactions will output these in this specific way.
        chemical_formula_number_regex = re.compile(
            r'^(\w+) \((\d+)\).*'
        )
        
        chemical_formula_number_match = \
            chemical_formula_number_regex.match(in_formula_with_number)
        if chemical_formula_number_match:
            molecule_formula = chemical_formula_number_match.group(1)
            molecule_number = int(chemical_formula_number_match.group(2))
            return (molecule_number, molecule_formula)
       
        print each_mol_with_num+' strangely did not match!'
        return False

def tests():
    reactions = Reactions_Wrapper()
    reactions.load('test.rxns')
   
    #for each_reaction in reactions:
    #    print reactions.iteration, each_reaction 
    
    assert reactions.parse_molecule_formula_with_number('H2O (1)') == \
            (1, 'H2O')

    assert reactions.parse_reaction_line('H (1) + OH (2) -> H2O (3)') == {'reactants': [(1, 'H'), (2, 'OH')], 'products': [(3, 'H2O')]}
    
    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

