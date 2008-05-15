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
from Struct import *

#Defining the format for XYZ file
ATOM_INDEX = 0
X_INDEX = 1
Y_INDEX = 2
Z_INDEX = 3

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
			self.rows.append(fields) #maybe we want to append fields as tuple
		f.close()

		print self.rows
		print type(self.rows)
		#print self.rows.transpose()

	def find_max_value(self):
		global X_INDEX, Y_INDEX, Z_INDEX

		#Python doesn't have switch-case statements yet so we just use
		#plain old if loops
		coordinate = coordinate.lower()
		if coordinate == 'x':
			column = X_INDEX
		elif coordinate == 'y':
			column = Y_INDEX
		elif coordinate == 'z':
			column = Z_INDEX
		
		max = Struct()
		max.x = 0
		max.y = 0
		max.z = 0
		for row in self.rows:
			if row[1] > max.x:
				max.x = row[1]
			if row[2] > max.y:
				max.y = row[2]
			if row[3] > max.z:
				max.z = row[3]

		#print max.x
		#print max.y
		#print max.z
		return max


	def normalize_coordinates(self):
		self.find_max_value()
		for row in self.rows:
			pass	

def main():
	Ethanol = XYZ()
	Ethanol.load('ethanol.xyz')
	Ethanol.normalize_coordinates()

if __name__ == '__main__':
	main()

