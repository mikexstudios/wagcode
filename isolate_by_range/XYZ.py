#!/usr/bin/env python
'''
XYZ.py
-----------------
A class to represent an XYZ file.
'''
__version__ = '0.1.0'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#from numpy import *
#import numpy
import math
from Struct import *

class XYZ:

    def __init__(self):
        pass
    
    '''
    self.rows format is:
    [atom type, x, y, z]
    '''
    def load(self, in_file):
        f = file(in_file)
        self.rows = []
        #self.rows.append(-1) #Make the 0th row nothing. We start from 1
        #Discard first two lines
        f.next()
        f.next()
        for line in f:
            fields = line.split()
            fields = map(str.strip, fields) #trim whitespace
            #Set (x,y,z) to floats
            fields[1] = float(fields[1])
            fields[2] = float(fields[2])
            fields[3] = float(fields[3])
            self.rows.append(fields) #maybe we want to append fields as tuple
        f.close()

        #print self.rows
        #print type(self.rows)
        #print self.rows.transpose()

    def find_max_value(self):
        max = Struct()
        max.x = self.rows[0][1] #Set to some initial value
        max.y = self.rows[0][2]
        max.z = self.rows[0][3]
        for row in self.rows:
            if row[1] > max.x:
                max.x = row[1]
            if row[2] > max.y:
                max.y = row[2]
            if row[3] > max.z:
                max.z = row[3]
        return max
    
    def find_min_value(self):
        min = Struct()
        min.x = self.rows[0][1] #Set to some initial value
        min.y = self.rows[0][2]
        min.z = self.rows[0][3]
        for row in self.rows:
            if row[1] < min.x:
                min.x = row[1]
            if row[2] < min.y:
                min.y = row[2]
            if row[3] < min.z:
                min.z = row[3]
        return min

    def normalize_coordinates(self):
        min = self.find_min_value()
        self.translate(-min.x, -min.y, -min.z)
        #print self.rows

    def translate(self, x, y, z):
        for index in xrange(len(self.rows)): #We don't need a copy of the row
            self.rows[index][1] += x
            self.rows[index][2] += y
            self.rows[index][3] += z

    '''
    Rotate all atoms about some coordinate.
    
    @param Struct (x, y, z) coordinates of the center point we will rotate around 
    @param string 'x', 'y', or 'z'
    @param float degrees of rotation about the specified axis given by left hand rule
    '''
    def rotate(self, with_respect_to_coord, axis, angle):
        #Determine which rotation matrix to use. We could use an all inclusive matrix
        #but I think this is easier:
        w = math.radians(angle) #The sin's and cos' use radian
        if axis == 'x':
            rotation_matrix = [
                [1.0, 0.0, 0.0],
                [0.0, math.cos(w), math.sin(w)],
                [0.0, -math.sin(w), math.cos(w)]
                ]   
        elif axis == 'y':
            rotation_matrix = [
                [math.cos(w), 0.0, -math.sin(w)],
                [0.0, 1.0, 0.0],
                [math.sin(w), 0.0, math.cos(w)]
                ]
        elif axis == 'z':
            rotation_matrix = [
                [math.cos(w), math.sin(w), 0.0],
                [-math.sin(w), math.cos(w), 0.0],
                [0.0, 0.0, 1.0]
                ]
        else:
            return #Do nothing

        #Translate to our center coordinate
        self.translate(-with_respect_to_coord.x, -with_respect_to_coord.y, -with_respect_to_coord.z)
        
        #Apply rotation
        for index in xrange(len(self.rows)): #We don't need a copy of the row
            #print self.rows[index]
            temp_row = self.rows[index][:1] #We have to create a temp since .extend() doesn't return.
            temp_row.extend(self.__multiply_matrix_by_vector(rotation_matrix, self.rows[index][1:]))
            self.rows[index] = temp_row
            del temp_row
            #print self.rows[index]

        #Undo the translation
        self.translate(with_respect_to_coord.x, with_respect_to_coord.y, with_respect_to_coord.z)
    
    '''
    Rotates all atoms about some given atom.

    @param integer Atom number (note that counting starts at 1).
    '''
    def rotate_wrt_atom(self, atom_number, axis, angle):
        if atom_number < 1 and atom_number > len(self.rows):
            return #Do nothing

        #Get the coordinates of the given atom. Minus 1 because we
        #start atom counting at 1 instead of 0.
        center_coord = Struct()
        center_coord.x = self.rows[atom_number-1][1]
        center_coord.y = self.rows[atom_number-1][2]
        center_coord.z = self.rows[atom_number-1][3]
        return self.rotate(center_coord, axis, angle)
    
    '''
    Adds an XYZ object to this one.

    @param in_molecule XYZ object representation of the molecule you want to add.
    '''
    def add(self, in_molecule):
        in_molecule_listrep = in_molecule.list_representation()
        self.rows.extend(in_molecule_listrep)
        #print self.rows

    def export(self, filename):
        f = file(filename, 'wb') #We open the file in binary mode so that newlines will be \n instead of DOS based
        #First line of XYZ file is the number of atoms
        f.write(str(len(self.rows)) + "\n")
        f.write("Generated by XYZ.py\n")
        #Now we write out each of the atoms
        for row in self.rows:
            #TODO: Maybe format the floats with printf or something so that
            #      they are all have the same spacing.
            row = map(str, row)
            f.write('    '.join(row) + "\n")
        f.close()
    
    def list_representation(self):
        return self.rows
    
    def return_sorted_by_atoms_dict(self):
        #Pre-sort the atoms by atom type (into a dictionary). This way, we don't
        #have to loop through the whole file every time we calculate distances for
        #a given atom.
        atoms_dict = {}
        for atom_number, each_row in enumerate(self.rows):
            #Correction to the atom_number since it starts at 1 instead of 0:
            atom_number += 1
            
            #We want our new list to be in the format:
            #atom_number x y z
            temp_list = [atom_number] #Put it in a list first. For some reason, 
            temp_list.extend(each_row[1:]) #can't combine these two on same line.
            
            #Now save it:
            try:
                atoms_dict[each_row[0]].append(temp_list)
            except KeyError:
                #This means that the dictionary entry for this atom has not been
                #created yet. So we create it:
                atoms_dict[each_row[0]] = [temp_list] #New list
        return atoms_dict

    def set_rows(self, in_rows):
        self.rows = in_rows
    
    '''
    TODO: Have this return something useful.
    '''
    def __str__(self):
        return ''

    '''
    Multiplies a matrix by a vector (both are represented by list data
    structure).

    Code from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/121574
    by Xunning Yue (19th April 2002)
    Note: There could possibly be a better way of doing this now in 2008.

    @param matrix
    @param vector
    @return list multiplied vector
    '''
    def __multiply_matrix_by_vector(self, m, v):
        nrows = len(m)
        ncols = len(m[0])
        w = [None] * nrows
        for row in range(nrows):
            sum = 0
            for col in range(ncols):
                sum += m[row][col]*v[col]
                w[row] = sum
        return w

def main():
    Ethanol = XYZ()
    Ethanol.load('ethanol.xyz')
    Ethanol.normalize_coordinates()
    Ethanol.export('ethanol2.xyz')

    Test = XYZ()
    Test.load('test.xyz')
    Ethanol.add(Test)

if __name__ == '__main__':
    main()

