#!/usr/bin/env python
'''
reax_connection_table.py
-----------------
A class to represent ReaxFF's fort.7 connection table. See the ReaxFF manual
for more info.

NOTE: The file pointer is not closed until the instance is deleted.

$Id$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
import sys #for exit
import re

class Connection_Table:
    iteration = 0 #Holds the current iteration we are working with.
    rows = []
    f = None #Will hold the file handle. Need to do this since no static vars.

    def __init__(self):
        pass

    def __del__(self):
        self.f.close()

    def __iter__(self):
        '''We want this to be iterable.'''
        return self
    
    def load(self, in_file):
        self.f = file(in_file)

    def next(self):
        '''
        Loads the next iteration into .rows and returns .rows. We can use this
        as part of an iterator.
        '''
        f = self.f #Just to simplify things
        #A helper/quick function to check for exactly float:
        def is_string_exactly_float(in_string):
            try:
                int(in_string)
            except ValueError:
                #This error means that the string is definitely not an integer.
                try:
                    float(in_string)
                    #Successful converting to a float!
                    return True
                except ValueError:
                    #A string that's neither an int or a float
                    return False
            return False

        #Make the 0th row nothing. We start from 1 so that it matches the numbering
        #of the atoms.
        self.rows = []
        self.rows.append(None) 
        
        #Process the iterations line. Sample line:
        #1005 a10a18_water                            Iteration:       0 #Bonds:  10
        iteration_regex = re.compile(r'^.+\s+Iteration:\s*(\d+)\s+.*')
        iteration_match = iteration_regex.match(f.next())
        if iteration_match:
            self.iteration = int(iteration_match.group(1))
        else:
            print 'ERROR: Iteration line could not be found!'
            sys.exit(1)
        
        #Try to detect where the last connection column is. To do this, we have
        #to sample the next line. There is no good way of returning the file
        #pointer to the line before since we are using file iterators which
        #buffer the stream. So we can process this line separately from the
        #loop.
        first_line = f.next()
        last_connection_column = self.detect_last_connection_column(first_line)
        fields = first_line.split()
        processed_fields = self.group_connect_and_bondorder_fields(fields,
                                                        last_connection_column) 
        self.rows.append(processed_fields) #maybe we want to append fields as tuple
        
        #Now iterate through the rest of the file:
        for line in f:
            fields = line.split()
            #Check to see if this is the end of the iterator block. We do that
            #by detecting if the line has exactly three items which are all
            #floats. Then if that's the case, we additionally check that the
            #next line after that has exactly one item that is a float. If so, we
            #know that we've reached the end of the iterator block.
            if len(fields) == 3 and \
               map(is_string_exactly_float, fields) == [True, True, True]:
                    #Now check the next line:
                    next_line = f.next()
                    next_fields = next_line.split()
                    if len(next_fields) == 1 and \
                       is_string_exactly_float(next_fields[0]) == True:
                        #We reached the end of the iterator block. Let's get out
                        #of this for loop!
                         break
            
            processed_fields = self.group_connect_and_bondorder_fields(fields,
                                                        last_connection_column) 
            self.rows.append(processed_fields) #maybe we want to append fields as tuple
        
        return self.rows

        #TODO: Close the file after there are no more iterations.
        #f.close()

    def group_connect_and_bondorder_fields(self, fields, last_connection_column):
        '''
        Takes fields list that was taken from the fort.7 file and returns a list
        where the first field is a sublist of connections and the second field
        is a sublist of bondorders.
        '''
        connect_fields = fields[:last_connection_column] #Want only the first i fields
        bondorder_fields = fields[last_connection_column:-3] #Don't want the last 3 cols
        #Now convert the types:
        try:
            connect_fields = map(int, connect_fields) #all the fields are integers
            bondorder_fields = map(float, bondorder_fields)
        except ValueError:
            print 'ERROR: There is a problem with converting the connect fields'+\
                    'to int and/or converting the bondorder fields to float!'
            sys.exit(1)
        #Put the connection part into a sub array so that it's easier to access. The
        #format is:
        # atom_number(ffield) [conn1, conn2, ...] molecule_number
        temp_fields = [connect_fields[1]] #Put in a list. This is the atom "number" (ffield) part.
        #At this step, we want to combine the connect fields with their corresponding
        #bond order. In other words, we want something like: [(4, '0.4123'), ...]. The
        #zip function does that for us.
        temp_fields.append(zip(connect_fields[2:-1], bondorder_fields)) #This is the connections part
        temp_fields.append(connect_fields[-1]) #This is the molecule number part
        return temp_fields

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

    #Testing detection of last connection column:
    line01 = '    1    9   13   16   18   22    0    0    0    0    0    0    1  0.709  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line01) == 13
    #print connect_table.detect_last_connection_column(line01)
    line02 = '    1    9   13   16   18   22    0    0    0    0    0    0    0  0.709  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line02) == 13
    line03 = '    1    9   13   16   18   22    0    0    0    0    0    0   48  0.000  0.713 0.706  0.699  0.000  0.000  0.000  0.000  0.000  0.000  4.042  0.000  1.440'
    assert connect_table.detect_last_connection_column(line03) == 13
    
    #A quick function to check for exactly float:
    #NOTE: Make sure that when we test this, that this is the same code as the
    #      one being used above!
    def is_string_exactly_float(in_string):
        try:
            int(in_string)
        except ValueError:
            #This error means that the string is definitely not an integer.
            try:
                float(in_string)
                #Successful converting to a float!
                return True
            except ValueError:
                #A string that's neither an int or a float
                return False
        return False
    
    #Testing string detection as float:
    assert is_string_exactly_float('2.4342') == True
    assert is_string_exactly_float('2.4342e-17') == True
    assert is_string_exactly_float('2') == False
    assert is_string_exactly_float('asdf') == False

    sample_end_line = '   1876.81413978385        1029.73076963256    3936.27567904897'
    sample_end_line = sample_end_line.split()
    assert map(is_string_exactly_float, sample_end_line) == [True, True, True]
    sample_end_line = '   1876.81413978385        1029    3936.27567904897'
    sample_end_line = sample_end_line.split()
    assert map(is_string_exactly_float, sample_end_line) == [True, False, True]


    print 'All tests completed successfully!'
    sys.exit(0)



def main():
    #tests()

    connect_table = Connection_Table()
    connect_table.load('fort.7')
    #connect_table.next()
    #print connect_table.iteration
    #connect_table.next()
    #print connect_table.iteration
    for i in connect_table:
        #print i
        print connect_table.iteration


if __name__ == '__main__':
    main()

