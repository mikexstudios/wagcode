#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
molecules_from_bo.py
-----------------
The purpose of this script is to return list of molecules from the first frame
of the connection table (ie. fort.7) given a bond order. This script helps us
determine what bond order we should use for the reax_reactions.py script.

This script uses the same control file as reax_reactions.

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
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
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: molcules_from_bo [controlfile] [bondorder]'
    print 'Since no control file specified, assuming the file is: control'
    control_file = 'control'

#Source the control file:
try:
    execfile(control_file)
except IOError: 
    print 'Error: '+control_file+' does not exist!'
    sys.exit(1)
print 'Read control file successfully: '+control_file

try:
    bondorder_cutoff = float(sys.argv[2])
    print 'Bond order cutoff specified at command line: '+str(bondorder_cutoff)
except IndexError:
    pass #Do nothing. We'll use the bond order in the control file.

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
    
    #Go to first frame:
    connection_table.next()

    all_molecules = molecule_helper.get_all_molecules()
    molecules_dict = molecule_helper.molecule_list_to_frequency_dict(all_molecules)
    
    print
    print 'List of molecules for the first frame in '+connection_table_file+\
          ' for the bond order: '+str(bondorder_cutoff)
    print '------------------------------------------------------'
    for molecule_formula, molecule_freq in molecules_dict.iteritems():
        print str(molecule_freq)+' x '+molecule_formula

def tests():
    #Put any tests here:   
      

    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
