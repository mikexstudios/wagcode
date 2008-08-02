#!/usr/bin/env python
'''
xmol_snapshot.py
-----------------
NOTE: There is currently no check for overbounds iteration when specifying
      an iteration rather than percent.

TODO: Add interval selection.
'''
__version__ = '0.1.0'
__date__ = '01 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys
#optparse is a pretty awesome command line parser!
#See: #http://docs.python.org/lib/module-optparse.html
from optparse import OptionParser
import os #uses path and rename stuff
#import time #for sleep
import signal #For fixing grep pipe issue
import re

#Parse command line options
usage = 'usage: %prog [iteration or percent]'
parser = OptionParser(usage=usage, version='%prog '+__version__)
(options, args) = parser.parse_args()
#print options
#print args

if len(args) != 1:
	parser.error('Need the [iteration or percent] argument')
else:
	in_iter_or_percent = args[0]

#Arguments
xmol_file = 'xmolout'
#iteration_regex = re.compile(r'^\s*.+?(\d+)\s+.+')

#Fixes the grep pipe error with python. See:
#http://mail.python.org/pipermail/python-list/2004-March/255270.html
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def main():
	#Figure out unique identifier string (second line of xmolout file).
	#Get the line:
	xmolout_f = file(xmol_file)
	xmolout_f.readline()
	xmolout_second_line = xmolout_f.readline()
	xmolout_f.close()
	#Extract unique id part:
	unique_id_regex = re.match(r'^\s*(.+?)\s+\d+\s+.+', xmolout_second_line)
	if unique_id_regex:
		unique_id = unique_id_regex.group(1).strip()
	else:
		print 'ERROR: Unique id could not be extracted from the second line of '+\
				'the '+xmol_file+'. Check the regex.'
		sys.exit(1)
	
	#Determine if we have a percent
	try:
		in_iter_or_percent.index('%')
		#We have percent. Now let's try to figure out the iteration.
		#Get the final iteration
		final_iteration_cmd = os.popen('tac '+xmol_file+' | grep "'+unique_id+'" | head -n 1')
		final_iteration_line = final_iteration_cmd.readline()
		final_iteration_cmd.close()
		#Extract final iteration
		final_iteration_regex = re.match(r'^\s*.+?\s+(\d+)\s+.+', final_iteration_line)
		if final_iteration_regex:
			final_iteration = int(final_iteration_regex.group(1))
		else:
			print 'ERROR: The final iteration could not be determined.'
			sys.exit(1)
		#Calculate what iteration the percent corresponds to:
		iteration_percent = int(in_iter_or_percent.strip('%')) * 0.01
		target_iteration = int(iteration_percent * final_iteration)
	except ValueError:
		#No percent, just iteration
		target_iteration = int(in_iter_or_percent)
	
	#Determine the closest iteration
	#First, determine the iteration interval
	second_iteration_cmd = os.popen('grep -n "'+unique_id+'" '+xmol_file+' | head -n 2')
	second_iteration_cmd.readline()
	second_iteration_line = second_iteration_cmd.readline()
	second_iteration_cmd.close()
	second_iteration_regex = re.match(r'^(\d+):\s*.+?\s+(\d+)\s+.+', second_iteration_line)
	if second_iteration_regex:
		#We assume the interval is constant and that the first iteration is 0.
		#So the interval is just second iteration - 0 = second iteration.
		iteration_interval = int(second_iteration_regex.group(2))
		iteration_line_interval = int(second_iteration_regex.group(1)) - 2
	else:
		print 'ERROR: The second iteration could not be determined.'
		sys.exit(1)
	
	#Now we calculate the closest iteration:
	whole_snapshop_number = target_iteration / iteration_interval
	remainer_snapshop_number = target_iteration % iteration_interval
	if float(remainer_snapshop_number)/iteration_interval >= 0.5:
		whole_snapshop_number += 1 #Round up
	#There is no 0th snapshot. They all start at 1.
	whole_snapshop_number += 1 

	#Now slice from that iteration
	end_line = whole_snapshop_number * iteration_line_interval
	xmol_slice_cmd = os.popen('head -n '+str(end_line)+' '+xmol_file+ \
		' | tail -n '+str(iteration_line_interval))
	for line in xmol_slice_cmd:
		print line
	xmol_slice_cmd.close()


if __name__ == '__main__':
	main()
