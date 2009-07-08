#!/exec/python/python-2.4.2/bin/python -u
'''
place_determiner.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '16 July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
import shutil
import time #For sleep
import re #For regex

#Arguments
run_first_pass_time = 1 #Minute(s)

def main():
	global run_first_pass_time

	print 'here'	


if __name__ == '__main__':
	main()
