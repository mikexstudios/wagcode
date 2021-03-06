#!/usr/bin/env python
'''
molfra_analysis.py
-----------------
Given a molfra.out file (information about molecules in the system)
from a ReaxFF simulation, outputs a tab separated file like:
[Iteration #]   [# of Molecule 1]   [# of Molecule 2]   [etc.]
This file can be then fed into gnuplot for visualization.

NEW: Now also outputs a tsv file with total number of molecules.
     Additionally creates gplot files that can be directly fed
	 into gnuplot for easy plotting of tsv data.

CHANGES:
0.2.1 - Fixed bug where graph line color not matched with name (since
        the name wasn't excluded).
0.2.0 - Added option to exclude molecules from molfra plot. Also auto-
        generates graphs by running gnuplot.
0.1.1 - Fixed line 147 regex to account for cases where Total Number
                  of molecules has extra whitespace.
'''
__version__ = '0.2.1'
__date__ = '30th July 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import re
import sys
import string
#optparse is a pretty awesome command line parser!
#See: #http://docs.python.org/lib/module-optparse.html
from optparse import OptionParser
import os #uses path and rename stuff
import time #for sleep

#Arguments:
molfra_file = 'molfra.out'
output_file = 'molfra.tsv'
num_mol_file = 'nummol.tsv'
gnuplot_file = 'molfra.gplot'
num_mol_gplot_file = 'nummol.gplot'
exclude_molecules = [] #Gets overridden by the command line option

#Regex for the iteration-freq-molecule lines:
num_mol_regex = re.compile('^\s+(\d+)\s+(\d+)\s+x\s+([a-zA-Z0-9]+)\s+[0-9\.]\s*');

#Parse command line options
usage = 'usage: %prog -g -s -l -e "mol1, mol2, ..."'
parser = OptionParser(usage=usage, version='%prog '+__version__)
parser.add_option('-e', '--exclude', dest='excludemolecules', 
                   help='List of molecules to exclude from the molfra plot.')
parser.add_option('-g', '--graphs', action='store_true', dest='generategraphs', 
                   help='Automatically generate gnuplot png graphs.')
parser.add_option('-s', '--smooth', action='store_true', dest='smoothlines', 
                   help='Instead of linespoints, uses line smoothing.')
parser.add_option('-l', '--large', action='store_true', dest='largeoutput', 
                   help='Large PNG graphic output 1024x768.')
(options, args) = parser.parse_args()
#print options
#print args

if options.excludemolecules:
	#Split by comma, then trim
	exclude_molecules = [i.strip() for i in options.excludemolecules.split(',')]
	for each_mol in exclude_molecules:
		print 'Excluding '+each_mol

############################################################
#Returns a list of all distinct molecules encountered in the
#molfra file.
############################################################
def get_all_molecules(f):
    global num_mol_regex
    molnames = {} #Dictionary/Hash of molnames
    
    f.seek(0) #start from beginning
    for line in f:
        matches = num_mol_regex.match(line)
        if(matches != None):
            molnames[matches.group(3)] = 0 #Just set some dummy value. We only want the key.

    return molnames.keys()            

################################################################
#Returns a dictionary with 0 as values for the input keys.
#Used to generate an empty molecule dictionary for each section.
################################################################
def create_empty_mol_dict(in_keys):
    mol_dict = {}
    for each_key in in_keys:
        mol_dict[each_key] = 0

    return mol_dict

############################
#This is our main execution:
############################
f = open(molfra_file)
fout = open(output_file, 'w')
fnummol = open(num_mol_file, 'w')

#Title for nummol file:
fnummol.write("Iteration\tTotal Number of Molecules\n")

#Get list of distinct molecules (1st pass).
#Also write titles to the output file
molnames = get_all_molecules(f)
mol_dict = create_empty_mol_dict(molnames)

#Delete the molecules we want to exclude.
#print exclude_molecules
for each_exclude in exclude_molecules:
	try:
		del mol_dict[each_exclude]
		print 'Excluded '+each_exclude
	except KeyError:
		print 'ERROR: Molecule '+each_exclude+' could not be found, so '+\
			  'not excluded'

print "All distinct molecules ("+str(len(mol_dict.keys()))+" total): \n"
print string.join(mol_dict.keys(), "\t")
fout.write(string.join(mol_dict.keys(), "\t")+"\n")

#Create GNUPlot file
fgplot = open(gnuplot_file, 'w')
fgplot.write("reset\n")
fgplot.write("set title \"Number of Molecules Analysis\"\n")
fgplot.write("set xlabel \"Time (iteration)\"\n")
fgplot.write("set ylabel \"Number of Molecules\"\n")
fgplot.write("set key outside below\n")
if options.smoothlines:
	pass #Use linesmoothing
else:
	fgplot.write("set data style linespoints\n")
if options.largeoutput:
	fgplot.write("set pointsize 2\n")
fgplot.write('plot ')
for i, each_molname in enumerate(mol_dict.keys()):
	if options.smoothlines:
		fgplot.write("'"+output_file+"' u 1:"+str(i+2)+" smooth bezier title \""+each_molname+"\"")
	else:
		fgplot.write("'"+output_file+"' u 1:"+str(i+2)+" title \""+each_molname+"\"")
    #Takes care of the last plot element (remove trailing ,)
	if(i != len(mol_dict.keys())-1):
		fgplot.write(", ") 
fgplot.write("\n")
if options.largeoutput:
	fgplot.write("set size 1.6,1.6\n") #1024x768 resolution
	fgplot.write("set term png\n")
else:
	fgplot.write("set term png\n")
fgplot.write("set output \"molfra.png\"\n")
fgplot.write("replot")
fgplot.close()
print "Gnuplot file written: "+gnuplot_file+"\n"

#Create Number of Molecules GNUPlot file
fgplot = open(num_mol_gplot_file, 'w')
fgplot.write("reset\n")
fgplot.write("set nokey\n")
fgplot.write("set title \"Total Number of Molecules Analysis\"\n")
fgplot.write("set xlabel \"Time (iteration)\"\n")
fgplot.write("set ylabel \"Total Number of Molecules\"\n")
#fgplot.write("set key outside below\n")
fgplot.write("set data style linespoints\n")
if options.largeoutput:
	fgplot.write("set pointsize 2\n")
fgplot.write("plot \""+num_mol_file+"\" u 1:2")
fgplot.write("\n")
if options.largeoutput:
	fgplot.write("set size 1.6,1.6\n") #1024x768 resolution
	fgplot.write("set term png\n")
else:
	fgplot.write("set term png\n")
fgplot.write("set output \"nummol.png\"\n")
fgplot.write("replot")
fgplot.close()
print "Gnuplot file written: "+num_mol_gplot_file+"\n"

#print molnames

#Read through each "section" of the file and extract the information
#we want.

f.seek(0)
f.next() #We skip the first two lines which is the bond order cutoff
f.next()

#num_molecules = [] #Keeps track of number of molecules over the iterations
current_iteration = -1 #Init value
mol_dict = create_empty_mol_dict(molnames)

while True:
	try:
		line = f.next()
	except(StopIteration):
		break #break out of while loop if we reached end of file
    
	matches = num_mol_regex.match(line)
	if(matches != None):
		#print matches.group(1)
		current_iteration = matches.group(1)
		#We want to get this data into the dictionary
		if(mol_dict.has_key(matches.group(3))):
			mol_dict[matches.group(3)] = matches.group(2)
		else:
			#This shouldn't happen (where we haven't already encountered
			#the key). Therefore, we should error.
			#Since version 0.2.0, this will occur when we are excluding
			#molecules. Therefore, commenting out.
			#print 'ERROR: '+matches.group(3)+' not in mol_dict!'
			pass

	##Delete the molecules we want to exclude.
	##print exclude_molecules
	#for each_exclude in exclude_molecules:
	#	try:
	#		del mol_dict[each_exclude]
	#		print 'Excluded '+each_exclude
	#	except KeyError:
	#		print 'ERROR: Molecule '+each_exclude+' could not be found, so '+\
	#			  'not excluded'

    #Match number of molecules
	matches = re.match('^\s+Total number of molecules:\s*(\d+)\s*', line);
	if(matches != None):
		#num_molecules.append(matches.group(1))
		fnummol.write(str(current_iteration)+"\t"+str(matches.group(1))+"\n")
    
    #The 'do' part of the loop:
	if(re.match('^Iteration Freq.+', line)):
		#print 'we are in do!'
		
		#Delete the molecules we want to exclude.
		#print exclude_molecules
		for each_exclude in exclude_molecules:
			try:
				del mol_dict[each_exclude]
				#print 'Excluded '+each_exclude
			except KeyError:
				print 'ERROR: Molecule '+each_exclude+' could not be found, so '+\
					  'not excluded'
		
		#We want to: 1. Write mol_dict to output file. 2. Clear mol_dict and iter.
		mol_dict_values = map(str, mol_dict.values()) #Assume it returns values in correct order
		#Perhaps some thing we can improve here is to have all zero values
		#be empty so that they aren't plotted in GNU plot
		fout.write(str(current_iteration)+"\t"+string.join(mol_dict_values, "\t")+"\n")
		
		#Clear values
		mol_dict_values = []
		mol_dict = create_empty_mol_dict(molnames)
		current_iteration = -1

fnummol.close()
fout.close()
f.close()

print 'Total number of molecules analysis generated in '+num_mol_file+". \n"
print 'Tab separated values file generated in '+output_file+". \n"

if options.generategraphs:
	#Run gnuplot to auto-generate png graphs:
	os.system('gnuplot '+gnuplot_file)
	print gnuplot_file+' graph generated!'
	time.sleep(1)
	os.system('gnuplot '+num_mol_gplot_file)
	print num_mol_gplot_file+' graph generated!'
	time.sleep(3)
	os.system('gqview')

'''
Sample Input:
Iteration Freq. Molecular formula               Molecular mass
   14500  11 x  C3H4O3                                88.0290
   14500   1 x  C7H8O9                               236.0550
   14500   2 x  C6H8O6                               176.0580
   14500   1 x  C5H8O4                               132.0600
   14500   1 x  C2H4                                  28.0320
   14500   1 x  CO2                                   43.9980
 Total number of molecules: 17
 Total number of atoms: 200
 Total system mass:  1760.58
Iteration Freq. Molecular formula               Molecular mass
   14600  11 x  C3H4O3                                88.0290
   14600   1 x  C7H8O9                               236.0550
   14600   2 x  C6H8O6                               176.0580
   14600   1 x  C5H8O4                               132.0600
   14600   1 x  C2H4                                  28.0320
   14600   1 x  CO2                                   43.9980
 Total number of molecules: 17
 Total number of atoms: 200
 Total system mass:  1760.58
'''
