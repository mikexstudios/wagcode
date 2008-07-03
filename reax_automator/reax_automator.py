#!/usr/bin/env python
'''
reax_automator.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '03 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments
import os.path #For file exist check and splitext

#Automator control file:
control_file_path = sys.argv[1]

if os.path.exists(control_file_path) == False:
	print 'Error: '+control_file_path+' does not exist!'
	exit(1)

#Source the control file:
simulation = [] #Pre-define as array
simulation.append(dict()) #Create the first element
string_substitutions = dict()
#This is not the best way of reading the config file since we have to re-read
#the whole file for each new simulation list element, but it's the most elegant 
#way to code. 
while True:
	try:
		execfile(control_file_path)
	except IndexError:
		simulation.append(dict())
		continue #Re-read the execfile
	break #Otherwise, there are no errors and we break out of this loop

#Now do the replaces for our strings:
def temp_replace_tags(in_dict):
	global string_substitutions
	temp_dict = dict()
	for sim_key, sim_value in in_dict.iteritems():
		#For each simulation control setting, we apply all of the defined
		#substitutions to it:
		for sub_key, sub_value in string_substitutions.iteritems():
			temp_dict[sim_key] = sim_value.replace(sub_key, sub_value)
	return temp_dict
simulation = map(temp_replace_tags, simulation) #Apply the func. to each simulation list element

print simulation
