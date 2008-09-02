#!/usr/bin/env python
'''
isolate_charges_from_atom_numbers.py
------------------------
Given a fort.56 file and a list of atom numbers, isolates the corresponding
lines.
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import sys
#import re
#import math

#Parameters
charges_file = 'fort.56'
atom_numbers_file = 'test_atom_numbers.txt'
output_file = 'test_isolated.charges'

def main():
    charges_f = file(charges_file)
    atom_numbers_f = file(atom_numbers_file)
    output_f = file(output_file, 'w')
    
    sum_charges = 0.0
    for atom_number in atom_numbers_f:
        atom_number = int(atom_number)
        charges_f.seek(0) #Need this so that we can keep iterating!
        for charge_line in charges_f:
            #Splits into: atom_number, charge
            charge_line_split = charge_line.split()
            charge_line_split[0] = int(charge_line_split[0])
            charge_line_split[1] = float(charge_line_split[1])
            
            #print atom_number, charge_line_split[0]
            if atom_number == charge_line_split[0]:
                #We have a match, let's output this line into new file
                #and sum the charges.
                output_f.write(charge_line)
                sum_charges += charge_line_split[1]

    charges_f.close()
    atom_numbers_f.close()
    output_f.close()

    print 'The sum of charges is: '+str(sum_charges)

if __name__ == '__main__':
	main()
