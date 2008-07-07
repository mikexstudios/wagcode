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
import time #For sleep

#Arguments
control_file_path = sys.argv[1] #Automator control file
job_id_sleep_time = 5 #Minutes
monitor_error_threshold = 3 #Number of times errors can occur in succession during monitoring before exit

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
		#TODO: Wait a bit:

	else:
		print 'ERROR: reax.run not found!'
		exit(1)
	
	#Get simulation information
	info_f = file('info.pbs')
	for line in info_f:
		cluster_regex = re.match(r'Cluster: (\s+)', line)
		jobid_regex = re.match(r'Job ID: (\d+).*', line)
		if cluster_regex:
			each_sim['cluster_name'] = cluster_regex.group(1)
			
		elif jobid_regex:
			each_sim['job_id'] = int(jobid_regex.group(1))

	#Monitor the simulation until it has completed.
	monitor_errors = 0
	while True:
		sq_cmd = os.popen('sq')
		#Sample line:
		#229142                slava    Running     4 30:12:19:22  Thu Jun 26 10:15:25
		for line in sq_cmd:
			sq_jobid_regex = re.match(r'(\d+)\s+.*', line)
			if int(sq_jobid_regex.group(1)) == each_sim['job_id']:
				#Job is still running. Sleep for a while.
				time.sleep(60*job_id_sleep_time) #In seconds
				monitor_errors = 0 #reset our errors
				continue
			elif os.path.exists('fort.90') and os.path.exists('fort.71'):
				#Simulation is complete. Breakout
				break
			else:
				#Must be an error
				if monitor_errors >= monitor_error_threshold:
					print 'ERROR: Unable to monitor simulation'
					exit(1)
				else:
					monitor_errors += 1
					continue
	
	#Finishing steps for the simulation that ended to prepare it for the next simulation.


		
	
