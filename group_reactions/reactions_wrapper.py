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
        #The \w in regex means alphanumeric and _
        chemical_formula_number_regex = re.compile(
            r'^(\w+) \((\d+)\).*'
        )
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
            split_by_arrow = line.split('->')
            reactions_side = split_by_arrow[0]
            products_side = split_by_arrow[1]

            reaction_molecules_with_num = reactions_side.split('+')
            product_molecules_with_num = products_side.split('+')

            #Parse the molecule number next to molecule chemical formula:
            reaction_molecules = []
            for each_mol_with_num in reaction_molecules_with_num:
                each_mol_with_num = each_mol_with_num.strip()
                chemical_formula_number_match = \
                    chemical_formula_number_regex.match(each_mol_with_num)
                if chemical_formula_number_match:
                    molecule_formula = chemical_formula_number_match.group(1)
                    molecule_number = chemical_formula_number_match.group(2)
                    #Add to our list as a tuple:
                    reaction_molecules.append(
                        (molecule_number, molecule_formula)
                    )
                else:
                    print each_mol_with_num+' strangely did not match!'

            #Do the same with product molecules. 
            product_molecules = []
            for each_mol_with_num in product_molecules_with_num:
                each_mol_with_num = each_mol_with_num.strip()
                chemical_formula_number_match = \
                    chemical_formula_number_regex.match(each_mol_with_num)
                if chemical_formula_number_match:
                    molecule_formula = chemical_formula_number_match.group(1)
                    molecule_number = chemical_formula_number_match.group(2)
                    #Add to our list as a tuple:
                    product_molecules.append(
                        (molecule_number, molecule_formula)
                    )
                else:
                    print each_mol_with_num+' strangely did not match!'

            #Now place this parsed reaction in our mapping data structure:
            reactants_to_products_mapping.append(
                {'reactants': reaction_molecules,
                 'products': product_molecules}
            )
        
        return reactants_to_products_mapping

def tests():
    reactions = Reactions_Wrapper()
    reactions.load('test.rxns')
   
    for each_reaction in reactions:
        print reactions.iteration, each_reaction 

    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

