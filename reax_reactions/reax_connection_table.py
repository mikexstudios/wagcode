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
import sys #for exit
import os #for os.SEEK_CUR

class Connection_Table:
    iteration = 0 #Holds the current iteration we are working with.
    rows = []
    f = None #Will hold the file handle. Need to do this since no static vars.

    def __init__(self):
        pass

    def __iter__(self):
        '''We want this to be iterable.'''
        return self
    
    def load(self, in_file):
        '''
        Loads the first iteration of the connection table file.

        Normally, fort.7 is the last iteration so most users will just call
        .load() and then use .rows. But there are cases when the fort.7 will be
        appended. In those cases, we won't want to load a hundreds of megabytes
        fort.7 file. We just load the first iteration.
        '''

        self.f = file(in_file)
        

    def next(self):
        '''
        Loads the next iteration into .rows and returns .rows. We can use this
        as part of an iterator.
        '''
        f = self.f #Just to simplify things

        #Make the 0th row nothing. We start from 1 so that it matches the numbering
        #of the atoms.
        self.rows = []
        self.rows.append(None) 
        
        #Process the iterations line. Sample line:
        #1005 a10a18_water                            Iteration:       0 #Bonds:  10
        iteration_regex = re.compile(r'^.+\s+Iteration:(\d+)\s+.*')
        iteration_match = iteration_regex.match(f.readline())
        if iteration_match:
            self.iteration = int(iteration_match.group(1))
        else:
            print 'ERROR: Iteration line could not be found!'
            sys.exit(1)

        
        #Try to detect where the last connection column is. To do this, we have
        #to sample the next line; then return to the original spot so that we
        #iterate over the lines.
        starting_position = f.tell()
        sample_line = f.readline()
        last_connection_column = detect_last_connection_column(sample_line)
        f.seek(starting_position)

        for line in f:
            #Check to see if this is 

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
        
        #TODO: Close the file after there are no more iterations.
        #f.close()
    
    def detect_last_connection_column(self, sample_line):
        '''
        Given a sample line from the fort.7 file, tries to detect where the last
        connection column is. This step is important since fort.7 file connection
        columns are variable. Thus, to keep the user from having to manually define
        where the connection column ends, we just try to detect it.
        '''
        #Try to detect where the last connection column is. We can guess it
        #by finding the spot where we see: [integer] [a float].
        sample_line = sample_line.split()
        for i, col in enumerate(sample_line):
            #We want to skip the atom number field. Hence the i > 2:
            try:
                if i > 2 and type(int(col)) == type(1): #match integer type
                    #Check for float in next col:
                    try:
                        int(sample_line[i+1])
                    except ValueError: #This is because int can't convert a float
                        float(sample_line[i+1]) #Check to see if we can float this
                        last_connection_column = i + 1 #Correct the fact we start at 0
                        return last_connection_column
                    except IndexError:
                        print 'ERROR: Could not determine last connection column.'
                        sys.exit(1)
            except ValueError: #We couldn't convert a float into an int
                pass #Ignore
        print 'ERROR: Could not determine last connection column.'
        sys.exit(1)

def tests():
    connect_table = Connection_Table()
    
    line01 = '    1    9   13   16   18   22    0    0    0    0    0    0    1  0.709  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line01) == 13
    #print connect_table.detect_last_connection_column(line01)
    
    line02 = '    1    9   13   16   18   22    0    0    0    0    0    0    0  0.709  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line02) == 13
    
    line02 = '    1    9   13   16   18   22    0    0    0    0    0    0   48  0.000  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line02) == 13
    
    print 'All tests completed successfully!'
    sys.exit(0)

def main():
    #tests()

    connect_table = Connection_Table()
    connect_table.load('fort.7')


if __name__ == '__main__':
    main()

