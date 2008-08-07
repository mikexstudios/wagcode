#!/usr/bin/env python
'''
reax_connection_table.py
-----------------
A class to represent ReaxFF's fort.7 connection table. See the ReaxFF manual
for more info.
'''
__version__ = '0.1.0'
__date__ = '05 August 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math

class Connection_Table:
	rows = []

	def __init__(self):
		pass
	
	def load(self, in_file):
		f = file(in_file)
		#Make the 0th row nothing. We start from 1 so that it matches the numbering
		#of the atoms
		self.rows.append(None) 
		#Discard the first line
		f.next()
		for line in f:
			fields = line.split()
			fields = fields[:8] #Want only the first 8 fields
			fields = map(str.strip, fields) #trim whitespace
			try:
				fields = map(int, fields) #all the fields are integers
			except ValueError:
				#We are probably on the last line where the values are floats
				continue #Skip to the next for loop
			
			#Put the connection part into a sub array so that it's easier to access. The
			#format is:
			# atom_number(ffield) [conn1, conn2, ...] molecule_number
			temp_fields = [fields[1]] #Put in a list. This is the atom "number" (ffield) part.
			temp_fields.append(fields[2:-1]) #This is the connections part
			temp_fields.append(fields[-1]) #This is the molecule number part

			self.rows.append(temp_fields) #maybe we want to append fields as tuple
		f.close()
		#print self.rows

def main():
	connect_table = Connection_Table()
	connect_table.load('fort.7')

if __name__ == '__main__':
	main()

