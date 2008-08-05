#!/usr/bin/env python
'''
reax_rdf.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '05 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
#import shutil
#import time #For sleep
import re #For regex
from XYZ import XYZ #XYZ class

#Arguments
control_file= sys.argv[1] #Settings for RDF

#Source the control file:
try:
	execfile(control_file)
except IOError: 
	print 'Error: '+control_file+' does not exist!'
	sys.exit(1)
print 'Read control file successfully: '+control_file

def main():
	#Read in XYZ file. Store all the coordinates.

	#Loop through each pair of atoms.
	
		#Calculate interatomic distances. Use the minimum image convention here to
		#take care of any periodic conditions. Since we are in this loop

	#Normalize the histrogram by comparing to ideal gas.



def get_minimum_image_distance(in_coord):


if __name__ == '__main__':
	main()
