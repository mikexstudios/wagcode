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

		#Try to detect where the last connection column is. We can guess it
		#by finding the spot where we see: 1 [a float].
		sample_line = f.next()
		sample_line = sample_line.split()
		for i, col in enumerate(sample_line):
			#We want to skip the atom number field. Hence the i > 2:
			try:
				if i > 2 and int(col) == 1:
					#Check for float in next col:
					try:
						int(sample_line[i+1])
					except ValueError: #This is because int can't convert a float
						float(sample_line[i+1]) #Check to see if we can float this
						last_connection_column = i + 1 #Correct the fact we start at 0
						break
					except IndexError:
						print 'ERROR: Could not determine last connection column.'
						sys.exit(1)
			except ValueError: #We couldn't convert a float into an int
				pass #Ignore
		
		#Reset file pointer to the beginning of the data lines:
		f.seek(0)
		f.next() #Discard first line
		for line in f:
			fields = line.split()
			fields = map(str.strip, fields) #trim whitespace
			connect_fields = fields[:last_connection_column] #Want only the first i fields
			bondorder_fields = fields[last_connection_column:-3] #Don't want the last 3 cols
			#Now convert the types:
			try:
				connect_fields = map(int, connect_fields) #all the fields are integers
				bondorder_fields = map(float, bondorder_fields)
			except ValueError:
				#We are probably on the last line where the values are floats
				continue #Skip to the next for loop
			
			#Put the connection part into a sub array so that it's easier to access. The
			#format is:
			# atom_number(ffield) [conn1, conn2, ...] molecule_number
			temp_fields = [connect_fields[1]] #Put in a list. This is the atom "number" (ffield) part.
			#At this step, we want to combine the connect fields with their corresponding
			#bond order. In other words, we want something like: [(4, '0.4123'), ...]. The
			#zip function does that for us.
			temp_fields.append(zip(connect_fields[2:-1], bondorder_fields)) #This is the connections part
			temp_fields.append(connect_fields[-1]) #This is the molecule number part

			self.rows.append(temp_fields) #maybe we want to append fields as tuple
		f.close()
		#print self.rows

def main():
	connect_table = Connection_Table()
	connect_table.load('fort.7')

if __name__ == '__main__':
	main()

