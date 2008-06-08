#!/usr/bin/env python
'''
get_multiple_etoh_energies.py
-----------------
Goes into each of the directories that we generated when we did an angle scan using
ReaxFF and extracts ENERGY line from fort.90
'''
__version__ = '0.1.0'
__date__ = '07 June 2008'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import os

#Arguments
folder_name_format = 'em_etoh01_[angle]deg'

def main():
	global folder_name_format

	f = file('angle_energies.txt', 'w') #Create shell script to convert to BGF and EM.
	f.write("Angle \t Energy \n")
	f.write("----------------------------------\n")

	for angle in range(0, 360, 15): #Change angle increment to suit your own need.
		current_folder_name = folder_name_format
		current_folder_name = current_folder_name.replace('[angle]', str(angle))
		cmd = os.popen("grep '^ENERGY' "+current_folder_name+"/fort.90")
		energy_line = cmd.read()
		cmd.close()
		#Remove the ENERGY part:
		energy_line = energy_line.replace('ENERGY', '')
		energy_line = energy_line.strip() #Trim whitespace
		#fort90 = file(current_folder_name+'/fort.90')

		#Write to file:
		f.write(str(angle)+" \t "+energy_line+"\n")

	f.close()
		


if __name__ == '__main__':
    main()
