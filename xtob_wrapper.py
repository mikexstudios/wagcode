#!/usr/bin/env python
'''
xtob_wrapper.py
-----------------
Wraps around Adri's xtob script so that it's easier to
convert .xyz files to .bgf (makes the process non-interactive.
'''
__version__ = '0.1.0'
__date__ = '08 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import pexpect
import sys
#optparse is a pretty awesome command line parser!
#See: #http://docs.python.org/lib/module-optparse.html
from optparse import OptionParser
import os #uses path and rename stuff
import time #for sleep

#Parse command line options
usage = 'usage: %prog -d [preset] -c "x y z" [file.xyz]'
parser = OptionParser(usage=usage, version='%prog '+__version__)
parser.add_option('-d', '--crystaldefault', dest='crystaldefault', 
                   help='Selects a crystal default cell dimensions.')
parser.add_option('-c', '--crystaldim', dest='crystaldim',
                   help='Sets crystal cell dimensions. Put x, y, z in quotes \
				   separated by space.')
(options, args) = parser.parse_args()
#print options
#print args

if len(args) != 1:
	parser.error('Need the [file.xyz] argument')
else:
	xyzfilename = args[0]

if options.crystaldefault:
	if options.crystaldefault == 'tio2_6x6':
		crystaldim = '19.49070 17.75400 50.00000'
if options.crystaldim:
	crystaldim = options.crystaldim


child = pexpect.spawn('xtob')
#child.logfile = sys.stdout
child.expect('\s*Input file in .xyz-format\s*')
child.sendline(xyzfilename)
child.expect('\s*Do you want to input cell parameters \(y/n\) \?\s*')
#Check if crystaldim has been set
try:
	crystaldim #Make sure this exists
	child.sendline('y')
	child.expect(' x y z dimensions periodic box in Angstrom')
	child.sendline(crystaldim)
	child.expect(' a b c angles periodic box in degees')
	child.sendline('90 90 90')
except NameError:
	child.sendline('n') 

child.expect(' Which option \(0-3\) ?')
child.sendline('0')

time.sleep(2) #Delay by 1 sec so that fort.15 can be created.

#Check if fort.15 exists:
#if os.path.isfile('fort.15'):
try:
	(noext_filename, ext) = os.path.splitext(xyzfilename)
	#print noext_filename
	os.rename('fort.15', noext_filename+'.bgf')
	os.unlink('fort.16')
	print 'Conversion succeeded: '+noext_filename+'.bgf created!'
except OSError:
	print 'fort.15 output file could not be found. Conversion failed!'
	exit(1)
