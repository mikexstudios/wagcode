#!/usr/bin/env python
'''
create_twists.py
-----------------
Takes output lowest adjacency structures and now applies 180 deg twists to them
in order to minimize the amount of steric clash. See my notebook Vol 2, p45-46 for
explanation of the algorithm.
'''
__version__ = '0.1.0'
__date__ = '23 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import math #for ceil
#import sqlite3

#Arguments

#Used to break out of nested for loops. See:
#http://mail.python.org/pipermail/python-list/2002-January/123692.html
class BreakLoop(Exception): pass 

def create_twists(surf_rep):
    '''We assume that the horizontal rows have the steric clash.'''
    #If row is odd, then there will be infinite recursion. So we'll
    #check for that first.
    if len(surf_rep[0]) % 2 == 1: #There is a remainder after divided by 2
        print 'ERROR: The surface representation row length is ODD. This'+ \
                'means that you cannot twist everything so that there are'+ \
                'no steric horizontal clashes'
        return surf_rep

    no_clashes = True #If it's false until the end, then we just return.
    try:
        for row_index, row in enumerate(surf_rep):
            for spot_index, each_spot in enumerate(row):
                if each_spot == 1 or each_spot == -1:
                    #Check the spot to the current position's right. We use modulus 
                    #to create the periodic wrap around effect. 
                    #ie. 0%2=0, 1%2=1, 2%2=0, 3%2=1, 4%2=0.
                    if surf_rep[row_index][(spot_index+1) % len(row)] == each_spot:
                        #print row_index, spot_index
                        no_clashes = False
                        #If the spot to the right is the same, then we need to invert
                        #that whole column.
                        for i in xrange(len(surf_rep)):
                            surf_rep[i][(spot_index+1) % len(row)] *= -1
                        #print surf_rep
                        #Now that we made a change, let's go back to the beginning
                        #and check everything again:
                        raise BreakLoop
    except BreakLoop:
        pass #Do nothing, since we set no_clashes to False, we will recurse

    
    if no_clashes == False:
        #We run it through another check
        print 'Doing another pass...'
        return create_twists(surf_rep)
        pass
    
    #Otherwise, everything is fine:
    return surf_rep



def main():
    etoh18 = [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
    etoh18 = [[0, 1, 0, 1, 0, 1], [1, 0, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
    etoh18 = [[0, 1, 0, 1, 0, 1], [0, 1, 1, 0, 1, 1], [1, 0, 1, 1, 1, 0]]
    #etoh18 = [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
    print create_twists(etoh18)

if __name__ == '__main__':
    main()
