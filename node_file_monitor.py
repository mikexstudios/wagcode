#!/usr/bin/env python
'''
node_file_monitor.py
-----------------
Given inputs of: in directory (where the files to be monitored are located),
out directory (where the files to be monitored will be copied), a list of files,
and a time interval, this script copies those files to the out directory every
time inverval.

Why would you use this? This script was written to monitor certain files stored
in the temp directory of a node when using PBS. The script copies those files to
your directory in hulk so that you don't have to manually log into each node 
just to check up on the progress of a few files.

NOTE: This doesn't need to be used anymore since my submission generating
      scripts (ie. mkreaxsub) also provide file copy to/from the node helper
	  scripts which completely eliminate the need for this file monitoring
	  script. (It's sad since I spent like a whole day writing this.)

NOTE: rsync is used to update the files. This saves redundancy in copies.
'''
__version__ = '0.1.0'
__date__ = '3 March 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#optparse is a pretty awesome command line parser!
#See: #http://docs.python.org/lib/module-optparse.html
from optparse import OptionParser 
#import optparse
import os #For path checks and stat
import string #Needed to pass this as an object into map
import time #For sleep and time
import sys #For exit

#Arguments (these will be set by the command line parser)
input_dir = ''
output_dir = ''
files = [] #A list of filenames
update_time = 5 #In minutes.
rsync_cmd = 'rsync -aq' #a = archive/recurse/preserve mode. q = less verbose
max_updates = 3000 #Just in case the process goes crazy
unchanged_threshold = 2 #Number of files the files are unchanged before script exits.
missing_file_threshold = 2 #Number of files we can't find the file before script exists.
last_update_time = time.time() #Just populate with current time for now

def main():
	#Globals
	global input_dir, output_dir, files, update_time
	global max_updates
	global unchanged_threshold
	
	#Parse command line options
	usage = 'usage: %prog -i [path] -o [path] -f "[filename1], [filename2]" -t [minutes]'
	parser = OptionParser(usage=usage, version='%prog '+__version__)
	parser.add_option('-i', '--inputdir', dest='inputdir', 
	                   help='Full path where the files to be monitored are located.')
	parser.add_option('-o', '--outputdir', dest='outputdir',
	                   help='Full path where the monitored files will be copied to.')
	parser.add_option('-f', '--files', dest='files',
	                   help='List of files (file1, file2, ...) to be monitored.')   
	parser.add_option('-t', '--time', dest='time', type='int', 
	                   help='[Optional] Time interval (in integer minutes) between files update. Default is 5 min.')
	(options, args) = parser.parse_args()
	#print options
	
	#Argument checking:
	#len doesn't work on options for some reason.
	#if len(options) < 3:
	#	parser.error('Incorrect number of arguments.')
	if options.inputdir:
		if os.path.exists(options.inputdir):
			input_dir = options.inputdir.rstrip('/') #Remove any / at end of path.
		else:
			parser.error('Input path does not exist!');
	else:
		parser.error('Input path not specified!');
		
	if options.outputdir:
		if os.path.exists(options.outputdir):
			output_dir = options.outputdir.rstrip('/')
		else:
			parser.error('Output path does not exist!');
	else:
		parser.error('Output path not specified!');
	
	if options.files:
		#Split into individual files
		options.files = options.files.strip(', ') #Trim , and space at ends
		files_temp = options.files.split(',')
		files_temp = map(string.strip, files_temp) #Trim filename whitespace
		#Existance of each file is checked on every update.
		files = files_temp
	else:
		parser.error('Files to monitor not specified!')
		
	if options.time:
		update_time = options.time
		#Don't need an else since we have a default already set

	
	#Okay, everything is good, let's run stuff!
	'''
	print input_dir
	print output_dir
	print files
	print update_time
	'''
	not_updated_count = 0 #Keeps track of the times the files monitored haven't been updated
	for i in range(1, max_updates):
		print 'Updating...'
		is_updated = update_files()
		if is_updated == False:
			not_updated_count += 1
		else:
			not_updated_count = 0 #We reset once we know that we have updated
		#Check to see if we reached the threshold
		if not_updated_count >= unchanged_threshold:
			sys.exit(0)
		#Otherwise, pause for the specified minutes and repeat!
		if i == 1:
			#We do this so that the first file shows up faster.
			time.sleep(10) #secs
		else:
			time.sleep(60*update_time)
		

file_not_found_count = 0 #Python doesn't have static vars so we use a global.
def update_files():
	global input_dir, output_dir, files
	global rsync_cmd
	global last_update_time
	global missing_file_threshold
	
	global file_not_found_count
	
	#Just run rsync for each of the files
	return_flag = False #If true, means >= 1 file has changed
	for each_file in files:
		#Check for file existance. If at least one file is missing, we exit the 
		#script. Maybe there can be an option to set where all of the files must
		#be missing for the script to end.
		if not os.path.exists(input_dir+'/'+each_file):
			print input_dir+'/'+each_file+' does not exist!'
			#We implement a threshold for missing files since sometimes this file
			#monitor is run before the simulations are run (so no output files are
			#generated yet).
			if file_not_found_count >= missing_file_threshold:
				print "We've reach the threshold for missing file. Exiting..."
				sys.exit(0)
			else:
				file_not_found_count += 1
		else:
			file_not_found_count = 0 #reset
			
		
		#Check if files have changed.
		file_stats = os.stat(input_dir+'/'+each_file)
		#[8] contains the modified time of file. The last_update_time holds the time
		#we last performed this check
		if file_stats[8] > last_update_time:
			print 'File has been updated!'
			print os.system(rsync_cmd+' '+input_dir+'/'+each_file+' '+output_dir+'/'+each_file)
			last_update_time = time.time() #Update the time
			return_flag = True
		else:
			print 'File has not been updated!'
			#We don't set the return_flag here.
		
	return return_flag


if __name__ == '__main__':
	main()
