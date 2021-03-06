#!/usr/bin/env python
'''
get_score.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '01 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import os #for path.isfile
import sqlite3

#Arguments
output_file = 'get_score.txt'
max_horizontal_spots = 6 #This allows us to convert the long string into an array of strings.
db_file = 'surface_adjacency.db'

def convert_bin_string_to_list(bin_string):
	global max_horizontal_spots
	
	max_iter = len(bin_string)/float(max_horizontal_spots)
	max_iter = int(math.ceil(max_iter)) #We want to round up so that our loop goes through the full string
	bin_list= []
	bin_string = list(bin_string) #We put each character in its own list element
	bin_string = map(int, bin_string) #Convert each element to int
	
	#Note for this method, it doesn't necessarily return a rectangular 2D list.
	for i in range(max_iter):
		bin_list.append(bin_string[0:max_horizontal_spots])
		bin_string = bin_string[max_horizontal_spots:] #Rest of the list
	
	return bin_list

def main():
	global output_file
	global db_file
	global db
	
	#Connect to our sqlite database. 
	if os.path.isfile(db_file):
		conn = sqlite3.connect(db_file)
		conn.row_factory = sqlite3.Row #Allows us to access rows by column name
		db = conn.cursor()
	else:
		print 'Database file not found: '+db_file
		exit()
	
	f = file(output_file, 'w')
	f.write("Best of each number of molecules:\n")
	f.write("# Mol \t Config \t Horiz. Adj. \t Vert. Adj. \t Score\n")
	f.write("----------------------------------------------------------------\n")
	#Make a table of the best score in each category:
	for each_num_mol in range(0,19): #0 to 18
		#db.execute('SELECT * FROM surf_configuration WHERE num_mol = ? ORDER BY score DESC LIMIT 1', (each_num_mol,))
		db.execute('''
			SELECT * FROM surf_configuration
		    WHERE num_mol = ?
			ORDER BY score ASC
			LIMIT 1
			''', (each_num_mol,))
		row = db.fetchone()
		print str(row['num_mol'])+"\t"+str(row['config'])+"\t"+str(row['horizontal_adjacencies'])+\
				"\t"+str(row['vertical_adjacencies'])+"\t"+str(row['score'])
		f.write(str(row['num_mol'])+"\t"+str(row['config'])+"\t"+str(row['horizontal_adjacencies'])+
				"\t"+str(row['vertical_adjacencies'])+"\t"+str(row['score'])+"\n")

	f.close()
	
	db.close()
	conn.close()

if __name__ == '__main__':
	main()
