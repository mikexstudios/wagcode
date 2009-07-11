"""
Crystal Trimmer
---------------
Given a bgf crystal file and the target z-height, this script trims off
the top and bottom of the z-heights in equal amounts to get to the target
z-height.

@author Michael Huynh (mikeh@caltech.edu)
@date 10th November 2007
"""

import sys, getopt #for argv
import re
import os.path #for filename splitting
import string

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'z:')
    except getopt.GetoptError:
        #print usage. Doesn't work for some reason
        print sys.argv[0]+' -z[target length] [filename]'
        sys.exit(2);

    target_z = float(opts[0][1])
    filename = args[0]

    #Now run stuff:
    f = open(filename);
    min_z, max_z = determine_z_extremes(f)
    crystal_height = max_z - min_z
    print 'Crystal height: '+str(crystal_height)
    #Sanity check
    if(crystal_height > target_z):
        print 'No point in trimming the crystal to below its real height! crystal_height > target_z!'
        sys.exit();
    #Calculate the amount we want to trim the crystal
    z_add_amount = (target_z - crystal_height)/2 #Divide by two since we only need to trim one side
    print 'Z baseline add amount: '+str(z_add_amount)
    adjust_z(f, min_z, z_add_amount, target_z)
    f.close()

def determine_z_extremes(in_file):
    min_z = 99999 #Initialize to something high
    max_z = -1 #Init to something low
    
    in_file.seek(0) #start from beginning of file
    for line in in_file:
        #Modify only HETATM lines
        if(re.match('^HETATM.+', line)):
            columns = re.split('\s+', line)
            #print columns
            #Determine the minimum z
            if(float(columns[5]) < min_z):
                min_z = float(columns[5])
                #print 'New min_z is: '+str(min_z)

            #Determine the max z
            if(float(columns[5]) > max_z):
               max_z = float(columns[5])
               #print 'New max_z is: '+str(max_z)
    return [min_z, max_z]

"""
Adjusts z column of bgf to half the target
"""
def adjust_z(in_file, min_z, add_amount, target_z):
    #We want to write to a new file
    in_file_name, in_file_ext = os.path.splitext(in_file.name)
    new_file = open(in_file_name+'_trim'+in_file_ext, 'wb') #We write in binary so that we can output unix line endings
    #print in_file_ext
    
    in_file.seek(0)
    for line in in_file:
        #print line
        if(re.match('^HETATM.+', line)):
            columns = re.split('(\s+)', line)
            #print columns
            columns[10] = float(columns[10])
            columns[10] = columns[10] - min_z + add_amount
            #NOTE: Below limits values to xx.xxxxx. If the cell is larger than 99,
            #then consider adjusting the value below
            columns[10] = '%8.5f' % columns[10] #add the 0's on the end of the decimal.
            #columns[10] = str(columns[10]
            #print columns
            new_file.write(string.join(columns, ''))
        elif(re.match('^CRYSTX.+', line)):
            columns = re.split('(\s+)', line)
            #print columns
            #Get z column
            columns[6] = float(columns[6])
            columns[6] = target_z
            columns[6] = '%8.5f' % columns[6]
            #columns[6] = str(columns[6])
            new_file.write(string.join(columns, ''))
        else:
            new_file.write(line)
            
    new_file.close()
            

if __name__ == "__main__":
    main()
