#!/usr/bin/env python
'''
dist_surf_track.py
-----------------
Given the specification of the surface (of a molecule in BGF format) and also
the atom to track, will output a list of distances the atom is from the surface
(the closest distance to a specified surface atom is tracked).
'''
__version__ = '0.1.0'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = ''
__copyright__ = 'General Public License (GPL)'

import sys
import re
import math

#Parameters
surface_z_min = 29    #Defines the starting z coordinates for the surface
surface_z_max = 33    #Defiles the ending z coordinates for the surface
target_surface_atom = 'Ti'
target_dye_atom = 'Ru'


def get_lines_per_iteration(in_file):
    f.seek(0)   #Start from beginning of file
    firstline = f.readline()
    #print firstline
    #print int(firstline)+1     #Turns out we don't have to regex. Just convert.
    return int(firstline)
    '''
    m = re.match('\s*(\d+)\s*', firstline)
    if(m):
        print int(m.group(1))+1
    else:
        print 'No lines per iteration found!'
        sys.exit()
    '''    

def split_each_iteration(in_file, lines_per_iteration):
    #all_lines = in_file.readlines(10000) #Add number here to limit lines read
    #print all_lines

    #We want to skip the lines_per_iteration and then start a new array
    in_file.seek(0)   #Start from beginning of file
    linecount = 1
    iteration = 1   #We start at 1 for clarity
    iter_lines = [] #Make array
    iter_lines.append([])   #Add array element. Need to continually do this.
    for line in in_file:
        #print linecount
        #print line
        #iter_lines[iteration-1].append(line)  #Add line to array
        if(linecount >= lines_per_iteration+3): #We add one to take into account the first two "junk" lines
            #print iter_lines[iteration-1]
            iteration+=1    #Increment
            iter_lines.append([])
            #iter_lines[iteration-1].append(line)  #Add line to array
            linecount=1
            #raw_input('Press any key then enter')
            #break
        iter_lines[iteration-1].append(line)  #Add line to array. Should place it here to make the output right...
        linecount+=1    #Increment linecount

    return iter_lines

def get_surface_atoms(iter_lines, z_min, z_max):
    iter_lines_split = []
    #Scan each line, split third column
    for line in iter_lines:
        #iter_lines_split.append(re.split('\s+', line))
        temp = re.split('\s+', line)
        #print temp
        #Ugly hack to eliminate out of array bounds error
        if(len(temp) >= 4):
            if((float(temp[3]) <= z_max) and (float(temp[3]) >= z_min)):
                iter_lines_split.append(temp)
    return iter_lines_split


def get_atom_position(iter_lines, in_atom):
    for line in iter_lines:
        temp = re.split('\s+', line)
        if(temp[0] == in_atom):
            return temp[1:]
        

def extract_atoms_from_list(split_iter_lines, in_atom):
    temp = []
    for line in split_iter_lines:
        if(line[0] == in_atom):
            temp.append(line)

    return temp

def calculate_distance(in_atom1_coord, in_atom2_coord):
    #Ugly hack to get rid of bad input data
    if(in_atom1_coord==None or in_atom2_coord==None):
        return 99
    
    #Pythagorean distance. Do two times for 3D.
    #print in_atom1_coord
    #print in_atom2_coord
    temp = math.sqrt((float(in_atom1_coord[0])-float(in_atom2_coord[0]))**2 +
                     (float(in_atom1_coord[1])-float(in_atom2_coord[1]))**2)
    #return temp
    return math.sqrt((float(in_atom1_coord[2])-float(in_atom2_coord[2]))**2 +
                     (temp)**2)
    
def get_min(dist_list):
    if(len(dist_list)<1):
        return -1
    
    #print dist_list
    return min(dist_list)   #There might be other implementations so we abstract it
    

#def get_surface_atoms(in_atomtype):
    #get third column



#def calculate_distance():


#Tests
#t1 = ['O    5.06871   0.75545  32.24738',
#      'O    5.06944   3.73249  32.24810',
#      'Ti   1.91727   0.76289  30.93942']
#print get_surface_atoms(t1,31,33)
#print get_atom_position(t1,'O')
#split_iter = get_surface_atoms(t1,29,33)
#print extract_atoms_from_list(split_iter, 'O')
#a1 = [1, 1, 1]
#a2 = [2, 2, 2]
#print calculate_distance(a1, a2)

#b1 = [1,2,3,4]
#print min(b1)   #Hm, but we can't see to do this since we can't get the idex.

#Main

f=open('xmolout')
lines_per_iter = get_lines_per_iteration(f)
#print lines_per_iter
iter_lines_list = split_each_iteration(f, lines_per_iter)
f.close()

distance_track_list = []
for iter_lines in iter_lines_list:
    #print iter_lines
    #sys.exit()
    all_surface_atoms = get_surface_atoms(iter_lines[2:], surface_z_min, surface_z_max)
    specific_surface_atoms = extract_atoms_from_list(all_surface_atoms, target_surface_atom)
    non_surface_target_atom = get_atom_position(iter_lines[2:], target_dye_atom)
    atom_distances = []
    for each_atom in specific_surface_atoms:
        atom_distances.append(calculate_distance(non_surface_target_atom, each_atom[1:]))
    #print atom_distances
    distance_track_list.append(get_min(atom_distances))
    
#print distance_track_list
f=open('distance_track.txt','w')
i=0
f.write("Iteration \t Distance (A)\n")
for distance in distance_track_list:
    print str(i)+"\t"+str(distance)
    f.write(str(i)+"\t"+str(distance)+"\n")
    i+=15
f.close()
