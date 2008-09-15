#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
grouped_reactions_wrapper.py
-----------------
Class that makes the .grprxns output file from reax_reactions an object
(specifically, an Iterator).

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #for exit
import re
from reax.reactions_wrapper import Reactions_Wrapper

class Grouped_Reactions_Wrapper:
    #Define some class variables:
    f = None #File handle for rxns file
    reactions_list = []
    grouped_reaction_number = 0
    reactions_wrapper = None

    def __init__(self):
        self.reactions_wrapper = Reactions_Wrapper()
        pass
    
    def __iter__(self):
        '''We want this to be iterable.'''
        return self
   
    def load(self, input_file):
        self.f = file(input_file)

        #Discard the first two informative lines
        self.f.next()
        self.f.next()
        #Discard the next two blank lines
        self.f.next()
        self.f.next()

    def next(self):
        '''
        Loads the next iteration of reactions and returns it. 

        Returns a list of tuples. The first element of the tuple is the
        iteration. The second element of the tuple is the reaction (as a
        dictionary). The dictionary has keys 'reactants'
        and 'products'. The values are tuples with first element being molecule
        number, second element being molecule formula. 
        
        Sample return:
        [
         (15, {'reactants': [(1, 'H'), (2, 'O')], 'products': [(3, 'H2O')]}),
         (30, {'reactants': ..., 'products': ...}), 
         etc.
        ]
        '''
        f = self.f #Just to simplify things
        reactions = []
        
        #Process the grouped reaction number line. Sample line:
        #Begin grouped reaction: 0
        grouped_reaction_number_regex = re.compile(r'^Begin grouped reaction: (\d+)')
        grouped_reaction_number_match = grouped_reaction_number_regex.match(f.next())
        if grouped_reaction_number_match:
            self.grouped_reaction_number = int(grouped_reaction_number_match.group(1))
            #Skip the next line which is just the divider line:
            #-------------------------------------------------
            f.next()
        else:
            print 'ERROR: Grouped reaction number line could not be found!'
            sys.exit(1)

        #Okay, now process all the reactions within this grouped reaction. We
        #detect the end of this grouped reaction through the separator:
        #----------------------------------
        end_grouped_reaction_regex = re.compile(r'^-+')

        for line in f:
            #Check for end of grouped reaction:
            if end_grouped_reaction_regex.match(line):
                #Throw out next two lines
                f.next()
                f.next()
                break
            
            #A sample line is like:
            #60: HO20Ti10(3) -> HO19Ti10(4) + O(5)
            #So we'll split by : first.
            split_by_colon = line.split(':')
            iteration = split_by_colon[0]
            reaction_line = split_by_colon[1]

            #Now parse the reaction line
            parsed_reaction_line = self.reactions_wrapper.parse_reaction_line(reaction_line)

            #Now place this parsed reaction in our mapping data structure:
            reactions.append(
                (iteration, parsed_reaction_line)
            )
        
        return reactions

def tests():
    grouped_reactions = Grouped_Reactions_Wrapper()
    grouped_reactions.load('test.grprxns')
   
    print grouped_reactions.next()
    print grouped_reactions.next()

    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    tests()

if __name__ == '__main__':
    main()

