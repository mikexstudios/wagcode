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
import os #For file exist check and splitext and path stuff
import shutil

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

#print simulation

#Now do stuff:
last_structure_folder = os.getcwd() #No trailing slash.
last_structure_filename = initial_structure #Assume initial_structure is same for both path and filename.
for each_sim in simulation:
	#Create output folder
	#if os.path.isdir(each_sim['output_folder']) == False:
	#	os.mkdir(each_sim['output_folder'])
	
	#Copy simulation files over. New folder will be created.
	shutil.copytree(each_sim['simulation_folder'], each_sim['output_folder'])

	#If first simulation, we copy initial structure over. Otherwise, copy last
	#structure over.
	shutil.copy(last_structure_path, each_sim['output_folder']) #file will be created in directory

	#Link last structure to geo. If windows, then we copy file instead of symlink:
	#if os.name == 'nt':
	#	shutil.copy(each_sim['output_folder']+'/'+last_structure_filename, each_sim['output_folder']+'/geo')
	#else:
	os.symlink(each_sim['output_folder']+'/'+last_structure_filename, each_sim['output_folder']+'/geo')
	
	#TODO: Do any extra stuff to the control file

	#Create submission script:
	filename_no_ext = os.path.splitext(last_structure_filename)[0]
	os.system('mkreaxsub '+filename_no_ext)

	#Submit the simulation
	if os.path.exists(last_structure_folder+'/reax.run'):
		os.system('rqsub '+submit_to_cluster+' reax.run')
	else:
		print 'ERROR: reax.run not found!'
		exit(1)
	
	#Get simulation information
	simulation_submit_number = 

	#Monitor the simulation until it has completed.
		
	
