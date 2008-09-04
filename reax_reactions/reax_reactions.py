#!/usr/bin/env python
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
from reax_connection_table import Connection_Table

#Arguments
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


if __name__ == '__main__':
    main()
