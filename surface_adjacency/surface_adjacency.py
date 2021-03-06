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
horizontal_adj_energy_cost = 20 #kcal/mol
vertical_adj_energy_cost = 10 #kcal/mol
hole_adjacency_cost = 1 #kcal/mol
horizontal_hole_cost = 3 #See p84 of Vol 2 of my notebook for more info.
horizontal_hole_near_cost = 2
db_file = 'surface_adjacency.db'

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

#'''
#Increase the surface by one spot in each direction to create a periodic effect.
#'''
#def feather_surface_periodic(surf_rep):
#   new_surf_rep = surf_rep[:]
#   #Add bottom row before top row
#   new_surf_rep.reverse()
#   new_surf_rep.append(surf_rep[-1])
#   new_surf_rep.reverse()
#   #Add top row after bottom row
#   new_surf_rep.append(surf_rep[0])
#
#   #Interchange rows with columns so that we can easily do the next part
#   #inverted_surf_rep = transpose_list(surf_rep)
#   inverted_new_surf_rep = transpose_list(new_surf_rep)
#   inverted_surf_rep = inverted_new_surf_rep[:]
#
#   #Add right column before left column
#   inverted_new_surf_rep.reverse()
#   inverted_new_surf_rep.append(inverted_surf_rep[-1])
#   inverted_new_surf_rep.reverse()
#   #Add left column after right column
#   inverted_new_surf_rep.append(inverted_surf_rep[0])
#   
#   return transpose_list(inverted_new_surf_rep)
#
##From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410687
#def transpose_list(lists):
#   if not lists: return []
#   return map(lambda *row: list(row), *lists)

def evaluate_adjacencies(surf_rep):
    #Create a copy of surf_rep so that it's not destroyed by the function
    surf_rep= [i[:] for i in surf_rep] 

    #Go through 2D array and determine the horizontal and vertical adjacencies
    #at each element. Then remove that element. Note that we are treating this 
    #like a periodic surface.
    horizontal_adjacencies = 0
    vertical_adjacencies = 0

    #Fake periodicity by actually increasing all the sides by 1 spot:
    #surf_rep = feather_surface_periodic(surf_rep)
    #print surf_rep

    for row_index, row in enumerate(surf_rep):
        #Skip the first and last row (put there by faking perodicity):
        #if row_index == 0 or row_index == len(surf_rep)-1:
        #   continue #Go to the next one, don't evaluate
        for spot_index, each_spot in enumerate(row):
            #Skip the first and last columns (put there by faking periodicity):
            #if spot_index == 0 or spot_index == len(row)-1:
            #   continue #Go to next one, don't evaluate

            if each_spot == 1:
                #Check adjacent spots. We use modulus to create the periodic
                #wrap around effect. ie. 0%2=0, 1%2=1, 2%2=0, 3%2=1, 4%2=0.
                if surf_rep[row_index][(spot_index-1) % len(row)] == 1:
                    horizontal_adjacencies += 1
                if surf_rep[row_index][(spot_index+1) % len(row)] == 1:
                    horizontal_adjacencies += 1
                #if surf_rep[row_index][(spot_index+1) % len(row)] == 1:
                #   horizontal_adjacencies += 1
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

    total_score += float(horizontal_adj_energy_cost) * horizontal_adjacencies
    total_score += float(vertical_adj_energy_cost) * vertical_adjacencies

    return total_score

def evaluate_holes(surf_rep):
    '''
    Assigns score to empty site placement on surface.

    See p49 and p84 of Vol. 2 of my notebook for more info.

    @return A tuple of 3 elements: (# of near horizontal holes, total number of
    horizontal holes, total number of hole adjacencies)
    '''
    #Create a copy of surf_rep so that it's not destroyed by the function
    surf_rep= [i[:] for i in surf_rep] 
    
    #Go through 2D array and determine the horizontal holes and adjacent holes
    #at each element. Then remove that element. Note that we are treating this 
    #like a periodic surface.
    horizontal_near = 0 #For distance of 0 or 1 apart
    horizontal_total = 0 #For total count of holes in same horizontal row.
    total_adjacencies = 0
   
    #Helper function
    def num_zeros_in_row(in_row):
        num_zeros = 0
        for i in in_row:
            if i == 0:
                num_zeros += 1
        return num_zeros
    
    def num_near_horizontal_holes(row):
        '''We define 'near' as 2 spots to the left or right'''
        num_near = 0
        for spot_index, spot in enumerate(row):
            if spot == 0:
                #Check spots to the left and right. We use the modulus to create
                #the periodic wrap around effect.
                if row[(spot_index-1) % len(row)] == 0:
                    num_near += 1
                if row[(spot_index+1) % len(row)] == 0:
                    num_near += 1
                if row[(spot_index-2) % len(row)] == 0:
                    num_near += 1
                if row[(spot_index+2) % len(row)] == 0:
                    num_near += 1
        return num_near


    #First, let's process the horizontal stuff:
    for row_index, row in enumerate(surf_rep):
        #How many 0's are in this row? If only 1, then we ignore. if more than
        #one, then we process:
        num_zeros = num_zeros_in_row(row)
        if num_zeros > 1:
            horizontal_total += num_zeros #number of holes we have in this row
            #Now check for adjacent or 1 space apart holes:
            horizontal_near += num_near_horizontal_holes(row)
        
    #Now let's process the adjacent hole stuff:
    for row_index, row in enumerate(surf_rep):
        for spot_index, each_spot in enumerate(row):
            if each_spot == 0:
                #Check adjacent spots. We use modulus to create the periodic
                #wrap around effect. ie. 0%2=0, 1%2=1, 2%2=0, 3%2=1, 4%2=0.
                #NOTE: We even check the diagonal spots!
                if surf_rep[row_index][(spot_index-1) % len(row)] == 0:
                    total_adjacencies += 1
                if surf_rep[row_index][(spot_index+1) % len(row)] == 0:
                    total_adjacencies += 1
                if surf_rep[(row_index-1) % len(surf_rep)][spot_index] == 0:
                    total_adjacencies += 1
                if surf_rep[(row_index+1) % len(surf_rep)][spot_index] == 0:
                    total_adjacencies += 1
                #Diagonal spots:
                if surf_rep[(row_index-1) % len(surf_rep)] \
                    [(spot_index-1) % len(row)] == 0:
                    total_adjacencies += 1
                if surf_rep[(row_index-1) % len(surf_rep)] \
                    [(spot_index+1) % len(row)] == 0:
                    total_adjacencies += 1
                if surf_rep[(row_index+1) % len(surf_rep)] \
                    [(spot_index-1) % len(row)] == 0:
                    total_adjacencies += 1
                if surf_rep[(row_index+1) % len(surf_rep)] \
                    [(spot_index+1) % len(row)] == 0:
                    total_adjacencies += 1


                #Now that we are done, remove the element we are looking at:
                surf_rep[row_index][spot_index] = 0

    return (horizontal_near, horizontal_total, total_adjacencies)

def score_holes(horizontal_near, horizontal_total, total_adjacencies):
    global horizontal_hole_near_cost, horizontal_hole_cost, hole_adjacency_cost
    hole_score = 0.0

    hole_score += float(horizontal_hole_near_cost) * horizontal_near
    hole_score += float(horizontal_hole_cost) * horizontal_total
    hole_score += float(hole_adjacency_cost) * total_adjacencies

    return hole_score

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
            horizontal_near INTEGER,
            horizontal_total INTEGER,
            total_hole_adjacencies INTEGER,
            score NUMERIC
        )
        ''')

    #print binary_string_permutation(6)
    placed_mol_binary_rep = binary_string_permutation(18)
    #placed_mol_binary_rep = ['111111111111111111']
    #placed_mol_binary_rep = ['0011']

    #Now we go through each one and evaulate the adjacencies
    #print 'Processing',
    for each_bin_rep in placed_mol_binary_rep:
        #Convert to 2 array of our surface sites:
        each_surf_rep = convert_bin_string_to_list(each_bin_rep)
        num_mol = get_num_occupied_spots(each_surf_rep)
        adjacencies = evaluate_adjacencies(each_surf_rep)
        (horizontal_near, horizontal_total, total_hole_adjacencies) = \
            evaluate_holes(each_surf_rep)
        score = 0
        score += score_adjacencies(adjacencies[0], adjacencies[1])
        score += score_holes(horizontal_near, horizontal_total, total_hole_adjacencies)

        #Insert into db:
        #print 'Inserted: '+str([num_mol, each_bin_rep, adjacencies[0], adjacencies[1], score])
        db.execute('INSERT INTO surf_configuration VALUES (NULL, ?, ?, ?, ?, ?,'
                    +'?, ?, ?)', 
            (num_mol, each_bin_rep, adjacencies[0], adjacencies[1],
             horizontal_near, horizontal_total, total_hole_adjacencies, score))
        #print '.',
    
    #Need to commit changes or else they will not be saved.
    conn.commit()
    #db.execute('SELECT * FROM surf_configuration')
    #print db.fetchall()
    db.close()
    conn.close()

if __name__ == '__main__':
    main()
