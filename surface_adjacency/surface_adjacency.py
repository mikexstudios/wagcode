#!/usr/bin/env python
'''
surface_adjacency.py
-----------------
'''
__version__ = '0.1.0'
__date__ = '18 May 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import math #for ceil
import sqlite3

#Arguments
max_horizontal_spots = 6 #This allows us to convert the long string into an array of strings.
horizontal_adj_energy_cost = 10 #kcal/mol
vertical_adj_energy_cost = 1 #kcal/mol
db_file = 'surface_adjacency2.db'

def binary_string_permutation(target_depth, previous_level_permutation=''):
	current_depth = len(previous_level_permutation)+1
	current_level_permutation = [previous_level_permutation+'0', previous_level_permutation+'1']
	if target_depth == current_depth:
		return current_level_permutation

	#Weird that I need to create a temporary list before I can extend it.
	temp_list = binary_string_permutation(target_depth, current_level_permutation[0])
	temp_list.extend(binary_string_permutation(target_depth, current_level_permutation[1]))
	return temp_list

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

def evaluate_adjacencies(surf_rep):
	#Go through 2D array and determine the horizontal and vertical adjacencies
	#at each element. Then remove that element. Note that we are treating this 
	#like a periodic surface.
	horizontal_adjacencies = 0
	vertical_adjacencies = 0

	for row_index, row in enumerate(surf_rep):
		for spot_index, each_spot in enumerate(row):
			if each_spot == 1:
				#Check adjacent spots. We use modulus to create the periodic
				#wrap around effect. ie. 0%2=0, 1%2=1, 2%2=0, 3%2=1, 4%2=0.
				if surf_rep[row_index][(spot_index-1) % len(row)] == 1:
					horizontal_adjacencies += 1
				if surf_rep[row_index][(spot_index+1) % len(row)] == 1:
					horizontal_adjacencies += 1
				#if surf_rep[row_index][(spot_index+1) % len(row)] == 1:
				#	horizontal_adjacencies += 1
				if surf_rep[(row_index-1) % len(surf_rep)][spot_index] == 1:
					vertical_adjacencies += 1
				if surf_rep[(row_index+1) % len(surf_rep)][spot_index] == 1:
					vertical_adjacencies += 1

				#Now that we are done, remove the element we are looking at:
				surf_rep[row_index][spot_index] = 0

	return [horizontal_adjacencies, vertical_adjacencies]		

def score_adjacencies(horizontal_adjacencies, vertical_adjacencies):
	global horizontal_adj_energy_cost, vertical_adj_energy_cost
	total_score = 0.0

	total_score += horizontal_adj_energy_cost * horizontal_adjacencies
	total_score += vertical_adj_energy_cost * vertical_adjacencies

	return total_score

'''
Since we are using 1,0 to represent occupied,unoccupied spots respectively,
we can just sum the 2D list to find out how many surface spots are occupied.
'''
def get_num_occupied_spots(surf_rep):
	return sum(map(sum, surf_rep))

def convert_list_to_bin_string(surf_rep):
	temp_list = []
	for each_rep in surf_rep:
		temp_list.extend(each_rep)
	return ''.join(temp_list)


def main():
	global db_file
	global db
	
	#Connect to our sqlite database. Create table if needed.
	conn = sqlite3.connect(db_file)
	db = conn.cursor()
	db.execute('DROP TABLE IF EXISTS surf_configuration')
	db.execute('''
		CREATE TABLE surf_configuration (
			id INTEGER PRIMARY KEY,
			num_mol INTEGER,
			config TEXT,
			horizontal_adjacencies INTEGER,
			vertical_adjacencies INTEGER,
			score NUMERIC
		)
		''')

	#print binary_string_permutation(6)
	#placed_mol_binary_rep = binary_string_permutation(4)
	placed_mol_binary_rep = ['111111111111111111']

	#Now we go through each one and evaulate the adjacencies
	for each_bin_rep in placed_mol_binary_rep:
		#Convert to 2 array of our surface sites:
		each_surf_rep = convert_bin_string_to_list(each_bin_rep)
		num_mol = get_num_occupied_spots(each_surf_rep)
		adjacencies = evaluate_adjacencies(each_surf_rep)
		score = score_adjacencies(adjacencies[0], adjacencies[1])

		#Insert into db:
		print 'Inserted: '+str([num_mol, each_bin_rep, adjacencies[0], adjacencies[1], score])
		db.execute('INSERT INTO surf_configuration VALUES (NULL, ?, ?, ?, ?, ?)', \
			(num_mol, each_bin_rep, adjacencies[0], adjacencies[1], score))
	
	#Need to commit changes or else they will not be saved.
	conn.commit()
	#db.execute('SELECT * FROM surf_configuration')
	#print db.fetchall()
	db.close()
	conn.close()

if __name__ == '__main__':
	main()
