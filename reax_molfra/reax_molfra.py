#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
molfra_analysis.py
-----------------
Given a molfra.out file (information about molecules in the system)
from a ReaxFF simulation, outputs a tab separated file like:
[Iteration #]   [# of Molecule 1]   [# of Molecule 2]   [etc.]
This file can be then fed into gnuplot for visualization.

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
#import re
import time #for sleep
from molfra_wrapper import Molfra_Wrapper

#Since we want to use /usr/bin/env to invoke python, we can't pass the -u flag
#to the interpreter in order to get unbuffered output. Nor do we want to rely on
#the environment variable PYTHONUNBUFFERED. Therefore, the only solution is to
#reopen stdout as write mode with 0 as the buffer:
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) 

#Arguments. Set some defaults before the control file in case the user does not
#define them.
exclude_molecules = []
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: reax_molfra [controlfile]'
    print 'Since no control file specified, assuming the file is: control'
    control_file = 'control'

#Source the control file:
try:
    execfile(control_file)
except IOError: 
    print 'Error: '+control_file+' does not exist!'
    sys.exit(1)
print 'Read control file successfully: '+control_file


def main():
    #Helper function:
    def create_empty_mol_dict(in_keys):
        '''
        Returns a dictionary with 0 as values for the input keys.
        Used to generate an empty molecule dictionary for each section.
        '''
        mol_dict = {}
        for each_key in in_keys:
            mol_dict[each_key] = 0
    
        return mol_dict
    
    molfra = Molfra_Wrapper()
    molfra.load(molfra_file)
    
    #We have to run two passes through the molfra.out file. The reason is that
    #we need to know in advance how many columns there will be.
    #FIRST PASS: Get column labels:
    all_molecule_formulas = molfra.get_all_unique_molecule_formulas()
    #Exclude our molecules here:
    all_molecule_formulas_set = set(all_molecule_formulas)
    for each_exclude in exclude_molecules:
        try:
            all_molecule_formulas_set.remove(each_exclude)
            print 'Excluded: '+each_exclude
        except KeyError:
            print 'Did not exclude since not found: '+each_exclude
    all_molecule_formulas = list(all_molecule_formulas_set)

    #SECOND PASS: Populate with the rows:
    iteration_nummol_moldict = []
    for each_mol_dict in molfra:
        all_mols_dict = create_empty_mol_dict(all_molecule_formulas)
        
        #Match the keys from the molecules we get back:
        for molecule_formula, molecule_freq in each_mol_dict.iteritems():
            try:
                all_mols_dict[molecule_formula] #This one is to check if key exists
                all_mols_dict[molecule_formula] = molecule_freq
            except KeyError:
                #We can't find this key, probably because we excluded this
                #molecule. Therefore, do nothing.
                pass

        #Put this in our big-ass list:
        iteration_nummol_moldict.append(
            (molfra.iteration,
             molfra.total_number_molecules,
             all_mols_dict)
        )


    #Now create our output files:
    print "All distinct molecules ("+str(len(all_molecule_formulas))+" total): \n"
    print "\t".join(all_molecule_formulas)

    #molfra.tsv and num_mol.tsv files:
    fmolfra = file(molfra_tsv_file, 'w')
    fnummol = file(num_mol_tsv_file, 'w')
    #Write headers for both:
    fmolfra.write("\t".join(all_molecule_formulas)+"\n")
    fnummol.write("Iteration\tTotal Number of Molecules\n")
    #Now write each row:
    for each_entry in iteration_nummol_moldict:
        iteration, num_mol, mol_dict = each_entry
        
        #For molfra.tsv:
        mol_dict_values = map(str, mol_dict.values()) #Assume it returns values in correct order
        #Perhaps some thing we can improve here is to have all zero values
        #be empty so that they aren't plotted in GNU plot
        fmolfra.write(str(iteration)+"\t"+"\t".join(mol_dict_values)+"\n")

        #For num_mol.tsv:
        fnummol.write(str(iteration)+"\t"+str(num_mol)+"\n")
    fmolfra.close()   
    fnummol.close()
    print 'Total number of molecules analysis generated in '+num_mol_tsv_file
    print 'Tab separated values file generated in '+molfra_tsv_file
    
    #Create GNUPlot script files:
    create_molfra_gplot_file(all_molecule_formulas)
    create_num_mol_gplot_file()
    
    if generate_graphs:
        #Run gnuplot to auto-generate png graphs:
        os.system('gnuplot '+molfra_gplot_file)
        print molfra_gplot_file+' graph generated!'
        time.sleep(1)
        os.system('gnuplot '+num_mol_gplot_file)
        print num_mol_gplot_file+' graph generated!'
        time.sleep(3)
        if view_immediately:
            os.system(display_program)

def create_molfra_gplot_file(all_molecule_formulas):
    fgplot = open(molfra_gplot_file, 'w')
    fgplot.write('''
reset
set title "Number of Molecules Analysis"
set xlabel "Time (iteration)"
set ylabel "Number of Molecules"
set key outside below
''')
    if smooth_lines == False:
        fgplot.write("set data style linespoints\n")
    if large_output == True:
        fgplot.write("set pointsize 2\n")
    fgplot.write('plot ')
    for i, each_molname in enumerate(all_molecule_formulas):
        if smooth_lines == True:
            fgplot.write("'"+molfra_tsv_file+"' u 1:"+str(i+2)+" smooth bezier title \""+each_molname+"\"")
        else:
            fgplot.write("'"+molfra_tsv_file+"' u 1:"+str(i+2)+" title \""+each_molname+"\"")
        #Takes care of the last plot element (remove trailing ,)
        if(i != len(all_molecule_formulas)-1):
            fgplot.write(", ") 
    fgplot.write("\n")
    if large_output == True:
        fgplot.write("set size 1.6,1.6\n") #1024x768 resolution
        fgplot.write("set term png\n")
    else:
        fgplot.write("set term png\n")
    fgplot.write("set output \"molfra.png\"\n")
    fgplot.write("replot")
    fgplot.close()
    print "Gnuplot file written: "+molfra_gplot_file

def create_num_mol_gplot_file():
    fgplot = open(num_mol_gplot_file, 'w')
    fgplot.write('''
reset
set nokey
set title "Total Number of Molecules Analysis"
set xlabel "Time (iteration)"
set ylabel "Total Number of Molecules"
set data style linespoints
''')
    if large_output:
        fgplot.write("set pointsize 2\n")
    fgplot.write("plot \""+num_mol_tsv_file+"\" u 1:2")
    fgplot.write("\n")
    if large_output:
        fgplot.write("set size 1.6,1.6\n") #1024x768 resolution
    fgplot.write("set term png\n")
    fgplot.write("set output \"nummol.png\"\n")
    fgplot.write("replot")
    fgplot.close()
    print "Gnuplot file written: "+num_mol_gplot_file+"\n"

def tests():

    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
