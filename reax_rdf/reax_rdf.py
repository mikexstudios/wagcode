#!/usr/bin/env python
'''
reax_rdf.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '05 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import os #For file exist check and splitext and path stuff
#import shutil
import time #For sleep
import math
#import re #For regex
from XYZ import XYZ #XYZ class
from reax_connection_table import Connection_Table

#Arguments
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: reax_rdf [controlfile]'
    sys.exit(0)

#Source the control file:
exclude_atoms_from_same_molecule = False
try:
    execfile(control_file)
except IOError: 
    print 'Error: '+control_file+' does not exist!'
    sys.exit(1)
print 'Read control file successfully: '+control_file

#Make sure some of our variables are in the correct format:
bin_size = float(bin_size)

def main():
    #Read in XYZ file. Store all the coordinates.
    simulation_atoms = XYZ()
    simulation_atoms.load(structure_file) #simulation_atoms.rows contains the data
    
    #Pre-sort the atoms by atom type (into a dictionary). This way, we don't
    #have to loop through the whole file every time we calculate distances for
    #a given atom.
    simulation_atoms_dict = {}
    for atom_number, each_row in enumerate(simulation_atoms.rows):
        #Correction to the atom_number since it starts at 1 instead of 0:
        atom_number += 1
        
        #We want our new list to be in the format:
        #atom_number x y z
        temp_list = [atom_number] #Put it in a list first. For some reason, 
        temp_list.extend(each_row[1:]) #can't combine these two on same line.
        
        #Now save it:
        try:
            simulation_atoms_dict[each_row[0]].append(temp_list)
        except KeyError:
            #This means that the dictionary entry for this atom has not been
            #created yet. So we create it:
            simulation_atoms_dict[each_row[0]] = [temp_list] #New list
    
    #Read in connection table (ReaxFF fort.7 style, see ReaxFF manual for more info)
    connection_table = Connection_Table()
    connection_table.load(connection_table_file)
    
    #Loop through each pair of atoms.
    distance_histogram = {} #Dictionary instead of array so we can add entries at any element.
    #TODO: I should add a try to this outer loop too to catch if from_atom
    #      doesn't exist in the dictionary
    for from_atom_row in simulation_atoms_dict[from_atom]:
        #Calculate interatomic distances. Use the minimum image convention here to
        #take care of any periodic conditions. We start by checking through all the
        #other atoms to see if they match our to_atom:
        try:
            for to_atom_row in simulation_atoms_dict[to_atom]:
                #Make sure this isn't the same atom by comparing atom number:
                if from_atom_row[0] == to_atom_row[0]:
                    continue
                
                #Make sure this to_atom isn't part of the same molecule. We figure
                #this out by using the molecule column of the connection table:
                if exclude_atoms_from_same_molecule:
                    if connection_table.rows[from_atom_row[0]][-1] == \
                       connection_table.rows[to_atom_row[0]][-1]:
                        #We have the same molecule. Don't do anything for this to_atom.
                        continue
                        #pass
                
                #Otherwise, calculate the interatomic distance:
                from_atom_coord = (from_atom_row[1], from_atom_row[2], from_atom_row[3])
                to_atom_coord = (to_atom_row[1], to_atom_row[2], to_atom_row[3])
                interatomic_distance = calc_interatomic_distance(from_atom_coord, to_atom_coord)
                #print interatomic_distance
                
                #Now figure out which bin this distance goes in. The algorithm in 
                #Simulation of Liquids by Allen (p182) differs from the algorithm in
                #Understanding Molecular Simulation by Frenkel (p86) in that Allen rounds
                #up (by adding 1) while Frenkel doesn't round up. Adri's RDF script
                #follows Allen's method. I will take the middle road and round the number:
                #(NOTE: This method is used because FORTRAN only had arrays so the bins
                #       have to be integers. We do it in this case because floats can't
                #       be exactly represented in any prog. language. So this int method
                #       is actually not too bad.
                distance_bin = int(round(interatomic_distance / bin_size))
                try:
                    #We add two for the contribution of both atoms because we just want
                    #to find the number of atoms within a certain distance of each other
                    #(also see p86 of Frenkel).
                    distance_histogram[distance_bin] += 2
                except KeyError:
                    #This is the first entry for this key. So we'll create it:
                    distance_histogram[distance_bin] = 2
        except KeyError:
            #to_atom was not found in the atoms dictionary
            print 'ERROR: '+to_atom+' was not found in the structure file: '+structure_file
            sys.exit(1)
    
    #print distance_histogram

    #Normalize the histrogram by comparing to ideal gas.
    #We want to compute (p184 Allen): 
    # g(r + 1/2 * delta_r) = n(b)/n_id(b) , no clue what b is though
    #where according to p183 Allen and corroborated by p86 Frenkel and Adri's RDF script:
    # n(b) = n_his(b)/(N * t_run)
    #In our case, we are only calculating from one static frame, so t_run = 1. The reason
    #why we divide by N is to get the "average". It sort of doesn't make sense to me since
    #this would make n(b) always fractional. But if n_id(b) is also fractional, then it
    #would work out.
    #Also according to p184 Allen:
    # n_id(b) = (4 pi rho)/3 * [(r + dr)^3 - r^3]
    #which makes sense. NOTE: To convert from the bin index to length (in angstroms) we 
    #reverse what we do by multiplying by the bin_size (aka delta_r).
    #Also, rho (the number density) is defined by wikipedia and MatDL wiki as:
    # rho = N/V ; (num of particles)/(volume of system)
    #where N is the number of particles we are considering.
    #But Adri's RDF script doesn't calculate rho this way. He does some sort of ratio
    #of the two atom populations...
    #total_number_atoms = len(simulation_atoms.rows)
    number_from_atoms = len(simulation_atoms_dict[from_atom])
    number_to_atoms = len(simulation_atoms_dict[to_atom])
    if from_atom == to_atom:
        total_number_analyzed_atoms = number_from_atoms
        #No combination correction factor:
        combination_correction_factor = 1
    else:
        total_number_analyzed_atoms = number_from_atoms + number_to_atoms
        #Calculate combination correction factor. This factor allows the ideal
        #gas approx to match the number of combinations that the n_his makes.
        #For more information, see p77 of Vol 2 of my notebook.
        heterogeneous_combinations = number_from_atoms * number_to_atoms
        homogeneous_combinations = \
         (total_number_analyzed_atoms * (total_number_analyzed_atoms-1)) / 2
        combination_correction_factor = \
         heterogeneous_combinations/float(homogeneous_combinations)
    total_number_molecules = connection_table.rows[-1][-1]
    total_volume = float(unit_cell[0]) * unit_cell[1] * unit_cell[2]
    rho = total_number_analyzed_atoms/total_volume
    g = {} #This is our pair correlation function results. However, have to store as bins, not angstroms
    
    for distance_bin, n_his in distance_histogram.iteritems():
        n = float(n_his)#/total_number_atoms
        #n = float(n_his)/total_number_molecules
        r = float(distance_bin) * bin_size #convert from bin index to length (angstroms)
        n_id = ((4 * math.pi * rho)/3) * ( (r + bin_size)**3 - r**3 )
        #Additional correction to n_id.
        n_id *= number_from_atoms + number_to_atoms
        n_id *= combination_correction_factor
        
        #print n, n_id
        g[distance_bin] = n/n_id
    
    #Now print it out with angstroms!
    #print "r \t g(r)"
    #for distance_bin, gr in g.iteritems():
    #   #The format syntax is that we have _____._____ (5 spots before the . and 5 spots
    #   #after). This will cover like 99.99% of all numbers we encounter.
    #   print "%10.5f \t %10.5f" % (float(distance_bin) * bin_size, gr)
    #   #pass

    #Output to file:
    try:
        output_f = file(output_file, 'w')
    except (NameError, IOError):
        print 'ERROR: Could not write output to '+output_file
        sys.exit(1)
    
    #Alternative method for printing it out. We print only for r <= 1/2 L, where L is
    #the average length of all the sides of the box. According to Deserno's paper on
    #calculating g(r) in 3-D, once we assume minimum image convention, the n_id term 
    #no longer increases like how we defined it above. So g(r) is only accurate to 1/2 L.
    average_L = (float(unit_cell[0]) + unit_cell[1] + unit_cell[2])/3
    max_bin = int(round((average_L/2) / bin_size)) #Convert to integer bin
    #print "r \t g(r)"
    output_f.write("r \t g(r)\n")
    for distance_bin in xrange(0, max_bin):
        #The format syntax is that we have _____._____ (5 spots before the . and 5 spots
        #after). This will cover like 99.99% of all numbers we encounter.
        try:
            #print "%10.5f \t %10.5f" % (float(distance_bin) * bin_size, g[distance_bin])
            output_f.write("%10.5f \t %10.5f\n" % (float(distance_bin) * bin_size, g[distance_bin]))
        except KeyError:
            #g doesn't have this distance_bin entry. No worries, since we know it is zero:
            #print "%10.5f \t %10.5f" % (float(distance_bin) * bin_size, 0.0)
            output_f.write("%10.5f \t %10.5f\n" % (float(distance_bin) * bin_size, 0.0))

    output_f.close()
    print 'RDF as tab separated values written to: '+output_file

    #Add in GNUPlot input file generation. Use below for smoothing:
    '''
    plot "[rdf_tsv_file]" u 1:2 with linespoints, \
         "[rdf_tsv_file]" u 1:2 smooth bezier
    '''
    gnuplot_template = '''
reset
set title "Radial Distribution Function"
set xlabel "r (angstrom)"
set ylabel "g(r)"
set nokey
plot "[rdf_tsv_file]" u 1:2 with linespoints
set term png
set output "[output_image_file]"
replot
'''
    try:
        gnuplot_template = gnuplot_template.replace('[rdf_tsv_file]', output_file)
        output_image_file = os.path.splitext(gnuplot_file)[0]+'.png'
        gnuplot_template = gnuplot_template.replace('[output_image_file]', output_image_file)
        #Write to file:
        gnuplot_f = open(gnuplot_file, 'w')
        gnuplot_f.write(gnuplot_template)
        gnuplot_f.close()
        print 'GNUPlot file written to: '+gnuplot_file

        #Now generate the graphs
        os.system('gnuplot '+gnuplot_file)
        print 'GNUPlot graph generated!'
        time.sleep(2)
        os.system('gqview')
    except IOError:
        print 'ERROR: Could not write gnuplot file to: '+gnuplot_file
    except NameError:
        #Do nothing
        pass
    


def calc_interatomic_distance(in_coord_a, in_coord_b):
    global unit_cell

    #Find the difference between the two coordinates in each of the axes:
    (ax, ay, az) = in_coord_a
    (bx, by, bz) = in_coord_b
    (dx, dy, dz) = (bx-ax, by-ay, bz-az)
    
    #Check to see if we have periodic conditions so that
    #we need to use the minimum image distance method.
    if type(unit_cell) == type(()) and unit_cell != False:
        (dx, dy, dz) = get_minimum_image_distance_each_axis((dx, dy, dz))
    
    #Compute the distance
    return math.sqrt(dx**2 + dy**2 + dz**2)

def get_minimum_image_distance_each_axis(distances): #distances is a tuple
    global unit_cell
    #The idea is that we assume that in_coord_a is at (0, 0, 0). Then if any of the
    #dimensions in in_coord_b are greater than 1/2 * L (where L is the corresponding
    #dimension of the unit cell), we use the "wrapped around" coordinate (which is
    #the one with the closer distance).
    
    #Now check to see if any of these distances are greater than or less than half of
    #the box length for that corresponding axis. Although we can use 'if' statements 
    #to check for this, a quicker method is to take advantage of arithmetic functions
    #which will encapsulate the same logic. See p29-30 of Simulation of Liquids by 
    #M. P. Allen for more information.
    (cellx, celly, cellz) = unit_cell
    (dx, dy, dz) = distances
    dx = dx - cellx * int(round(dx/cellx)) #The rounding is like: 0.49 -> 0; 0.51 -> 1.
    dy = dy - celly * int(round(dy/celly))
    dz = dz - cellz * int(round(dz/cellz))

    return (dx, dy, dz)


if __name__ == '__main__':
    main()
