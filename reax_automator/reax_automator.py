#!/exec/python/python-2.4.2/bin/python -u
'''
reax_automator.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '03 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
import shutil
import time #For sleep
import re #For regex

#Arguments
control_file_path = sys.argv[1] #Automator control file
job_id_sleep_time = 5 #Minutes
monitor_error_threshold = 3 #Number of times errors can occur in succession during monitoring before exit

#Need to put this function before control file reading so that
#the control file can call this.
def get_total_atoms(in_bgf_file):
	f = file(in_bgf_file)
	hetatm_regex = re.compile(r'^HETATM\s+(\d+)\s+.*')
	total_atoms = 0
	for line in f:
		hetatm_match = hetatm_regex.match(line)
		if hetatm_match:
			total_atoms = hetatm_match.group(1)
		elif re.match(r'(CONECT|END)', line):
			break
	f.close()

	return int(total_atoms)

#Need to move this outside of the main() function or else execfile()
#won't work properly.
if os.path.exists(control_file_path) == False:
	print 'Error: '+control_file_path+' does not exist!'
	sys.exit(1)

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
print 'Read control file successfully: '+control_file_path

def main():
	global control_file_path, job_id_sleep_time, monitor_error_threshold
	global initial_structure, simulation, string_substitutions
	
	#Now do the replaces for our strings:
	def temp_replace_tags(in_dict):
		global string_substitutions
		temp_dict = dict()
		for sim_key, sim_value in in_dict.iteritems():
			#For each simulation control setting, we apply all of the defined
			#substitutions to it. But for now, if sim_value is not a string,
			#then we'll just skip the replacing.
			if type(sim_value) != type(''): #string
				temp_dict[sim_key] = sim_value
				continue #skip this one
			for sub_key, sub_value in string_substitutions.iteritems():
				temp_dict[sim_key] = sim_value.replace(sub_key, sub_value)
		return temp_dict
	simulation = map(temp_replace_tags, simulation) #Apply the func. to each simulation list element
	print 'Completed string substitutions...'

	#Now do stuff:
	base_folder = os.getcwd() #No trailing slash.
	last_structure_folder = os.getcwd() #No trailing slash.
	last_structure_filename = initial_structure #Assume initial_structure is same for both path and filename.
	
	for each_sim in simulation:
		#Create output folder
		#if os.path.isdir(each_sim['output_folder']) == False:
		#	os.mkdir(each_sim['output_folder'])
		
		#Copy simulation files over. New folder will be created.
		shutil.copytree(base_folder+'/'+each_sim['simulation_folder'], each_sim['output_folder'])
	
		#If first simulation, we copy initial structure over. Otherwise, copy last
		#structure over.
		shutil.copy(last_structure_filename, each_sim['output_folder']) #file will be created in directory
		
		#Change directory to the output folder so that we don't have to 
		#keep prepending the output_folder var.
		os.chdir(each_sim['output_folder'])
		
		#Link last structure to geo. Note: The src argument is relative to
		#the path specified in the dst argument for some strange reason.
		os.symlink(last_structure_filename, 'geo')
	
		print 'Copied over simulation files and structure: '+each_sim['simulation_folder']
	
		#Now do file replacement stuff:
		try:
			eval_regex = re.compile(r'^eval:(.+)')
			for k, v in each_sim['replacements'].iteritems():
				f = file(k)
				temp_f = file(k+'.temp', 'w')
				for line in f:
					for each_replace in v:
						eval_match =  eval_regex.match(each_replace[1])
						if eval_match:
							line = line.replace(each_replace[0], str(eval(eval_match.group(1))))
						else:
							line = line.replace(each_replace[0], each_replace[1])
					temp_f.write(line)
				temp_f.close()
				f.close()
				shutil.move(k+'.temp', k) #Replace file with our temp one
			print 'Completed file replacements...'
		except KeyError:
			pass #Do nothing since this simulation did not define any replacements.
		
		#Create submission script:
		filename_no_ext = os.path.splitext(last_structure_filename)[0]
		os.system('mkreaxsub '+filename_no_ext)
	
		#Submit the simulation
		if os.path.exists('reax.run'):
			os.system('qsub reax.run')
			#Wait a bit (so that info.pbs can be generated)
			time.sleep(10) #Seconds
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
		print 'Got simulation information...'
		
		#Monitor the simulation until it has completed.
		monitor_errors = 0
		simulation_running = True
		while simulation_running == True:
			sq_cmd = os.popen('showq|grep $USER')
			#print 'New loop instance...'
			#Sample line:
			#229142                mikeh    Running     4 30:12:19:22  Thu Jun 26 10:15:25
			#This is the case where we only had one simulation running and
			#that simulation is now complete. So in order to get into the
			#for loop, we add an element to the command output.
			if sq_cmd.readline() == '':
				sq_cmd = ['']
			else:
				#There is no seek, so we reissue the command as a means
				#to reset.
				sq_cmd = os.popen('showq|grep $USER')
	
			for line in sq_cmd:
				sq_jobid_regex = re.match(r'(\d+)\s+.*', line)
				#Need to check sq_jobid_regex first in case we didn't match.
				if sq_jobid_regex and int(sq_jobid_regex.group(1)) == each_sim['job_id']:
					#Job is still running. Sleep for a while.
					print 'Simulation still running...'
					time.sleep(60*job_id_sleep_time) #In seconds
					monitor_errors = 0 #reset our errors
					break #Out of for loop
				elif os.path.exists('fort.90') and os.path.exists('fort.71'):
					#Simulation is complete. Breakout
					print 'Simulation complete!'
					simulation_running = False #Break out of while loop
					break
				else:
					print 'Error in monitoring: '+str(monitor_errors)
					#Must be an error
					if monitor_errors >= monitor_error_threshold:
						print 'ERROR: Unable to monitor simulation'
						sys.exit(1)
					else:
						monitor_errors += 1
						time.sleep(60*job_id_sleep_time) #sec
						break
		
		#Finishing steps for the simulation that ended to prepare it for the next simulation.
		if os.path.exists('fort.90'):
			try:
				shutil.copy('fort.90', each_sim['final_structure_name'])
				last_structure_filename = each_sim['final_structure_name']
			except KeyError:
				#Final structure name not defined
				last_structure_filename = 'fort.90'

		#Run finishing function if defined:
		try:
			eval(each_sim['finishing_function'])
			print 'Executed finishing function: '+each_sim['finishing_function']
		except KeyError:
			pass #Do nothing
				
	print 'Simulations successfully completed!'



if __name__ == '__main__':
	main()
