#!/usr/bin/env python
'''
fort71.py
-----------------
A class to represent an fort71 file.
   Iter. Nmol    Epot         Ekin      Etot        T(K)  Eaver(block) Eaver(total) Taver      Tmax    Pres(GPa)   sdev(Epot)  sdev(Eaver)    Tset      Timestep    RMSG     Totaltime
       0  13  41 -131669.06     927.29 -130741.78     300.56 -131669.06 -131669.06     300.56     300.56       0.00       0.00       0.00     300.00       0.25      11.35       0.00
      10  13  41 -131670.67     920.93 -130749.74     298.51 -131677.23 -131677.23     330.80     301.63      -0.37       3.45       1.42     300.00       0.25      10.81       2.75
      20  10  42 -131648.18     920.77 -130727.42     298.45 -131656.25 -131666.74     297.80     298.45      -0.30       7.51       3.79     300.00       0.25      11.14       5.25
'''
__version__ = '0.1.0'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import math
#from Struct import *
import os #For os.SEEK_END

#Constants:
HEADER_LINE_LENGTH = 183 #Characters in the first line (including \n char)
DATA_LINE_LENGTH = 182 #Characters in regular data lines (including \n char)

#File format (Specifies the column. Starts at 0):
EPOT = 3


class fort71:
	#Variable declarations
	f = None

	def __init__(self):
		pass
	
	def load(self, in_file):
		self.f = file(in_file)
		#Start after the first line
		self.f.seek(HEADER_LINE_LENGTH)
		#print self.f.readline()
	
	def goto_line(self, in_line):
		self.f.seek(HEADER_LINE_LENGTH + DATA_LINE_LENGTH * (in_line-1))
	
	def get_total_lines(self):
		self.f.seek(0, os.SEEK_END)
		last_line_pos = int(self.f.tell())
		return ((last_line_pos - HEADER_LINE_LENGTH)/DATA_LINE_LENGTH) - 1
	
	def get_lines_from(self, beg, end):
		self.goto_line(beg)

		#return self.f.readlines((end-beg) * DATA_LINE_LENGTH)

	def process_line(self, in_line):
		return in_line.split()

	def get_energy_average_and_sdev(self, beg, end):
		#Get rows first and process them:
		#rows = self.get_lines_from(beg, end)
		#print rows
		self.goto_line(beg)
		processed_rows = []
		for row in self.f:
			processed_rows.append(self.process_line(row))
			if len(processed_rows) > (end-beg): #> instead of >= since we want to include the end row
				break
		print processed_rows
		#Sum the energies
		total = 0
		for row in processed_rows:
			total += float(row[EPOT])
		#Find average:
		aver = float(total)/len(processed_rows)
		#Second pass: Find the deviation of each number from the mean. Then square that value.
		dev_from_mean_squared = []
		for row in processed_rows:
			dev_from_mean_squared.append((float(row[EPOT]) - aver)**2)
		#Sum the squares:
		#print dev_from_mean_squared
		#return
		sum_of_squares = sum(dev_from_mean_squared)
		#Square root (because it's RMS value):
		stdev = math.sqrt(sum_of_squares)

		return (aver, stdev)

		

def main():
	#Testing
	t = fort71()
	t.load('fort.71')
	print t.get_total_lines()
	print t.get_energy_average_and_sdev(1, 2)

if __name__ == '__main__':
	main()
