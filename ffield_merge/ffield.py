#!/usr/bin/env python
'''
ffield.py
-----------------
A class to represent ReaxFF's ffield file. See the ReaxFF manual
for more info.
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

#import math
import sys #for exit
import re
import itertools

def get_lines(f, start, end = None):
    '''
    Given a file stream and the start and end line numbers, returns an array
    with those lines. NOTE: Lines start at 1.

    @param f File stream
    @param start Starting line number (int). Must be >= 1.
    @param end Ending line number (int). If None, then selects to end of file.
    @return array of strings The specified lines in an array.
    '''
    f.seek(0) #reset to start of file
    #Error checking:
    if start < 1:
        raise ValueError
    if end != None and end < start:
        raise ValueError
    
    #Unlike iteration (which starts at 0), we denote line numbers as starting at
    #1. Therefore, subtract 1 from start here: 
    start -= 1
    #The way islice works is that it selects to the line right before end.
    #For instance, to select just the first line, we need to do islice(f, 1, 2).
    #Therefore, we need to subtract 1 from end.
   
    lines = []
    for i in itertools.islice(f, start, end):
        lines.append(i)

    return lines

def get_line(f, num):
    '''
    Given a file stream and a line number, returns that line as a string.
    NOTE: Lines start at 1.

    @param f File stream
    @param num Line number (int). Must be >= 1.
    @return string Line as a string.
    '''
    return get_lines(f, num, num)[0]

class Ffield:
    f = None #Will hold the file handle. Need to do this since no static vars.
    sections = {}

    def __init__(self):
        #For some strange reason, must initialize variables here. Otherwise,
        #they will share the same state as previously instantiated object! WTF!
        self.f = None
        self.sections = {}

    def __del__(self):
        #self.f.close()
        pass

    def load(self, in_file):
        self.f = file(in_file)

    def parse_sections(self):
        '''
        Given a file stream for ffield, parses the file into sections (ie. general
        parameters, atom params, angle params, etc.). Then returns a dictionary that
        includes all the sections.
    
        @param f File stream for ffield.
        @return dict Dictionary of sections. The key's are the section labels.
        '''
        #Identifiers for each section:
        #For general:
        #39       ! Number of general parameters                                        
        #For atom:
        #12    ! Nr of atoms; cov.r; valency;a.m;Rvdw;Evdw;gammaEEM;cov.r2;#            
        atom_regex = re.compile(r'! Nr of atoms')
        #For bonds:
        #58      ! Nr of bonds; Edis1;LPpen;n.u.;pbe1;pbo5;13corr;pbo6                  
        bond_regex = re.compile(r'! Nr of bonds')
        #For off-diagonal terms:
        #22    ! Nr of off-diagonal terms; Ediss;Ro;gamma;rsigma;rpi;rpi2               
        offdiag_regex = re.compile(r'! Nr of off-diagonal terms')
        #For angle terms:
        #83    ! Nr of angles;at1;at2;at3;Thetao,o;ka;kb;pv1;pv2                        
        angle_regex = re.compile(r'! Nr of angles')
        #For torsion terms:
        #58    ! Nr of torsions;at1;at2;at3;at4;;V1;V2;V3;V2(BO);vconj;n.u;n            
        torsion_regex = re.compile(r'! Nr of torsions')
        #For hydrogen bonds:
        #9    ! Nr of hydrogen bonds;at1;at2;at3;Rhb;Dehb;vhb1                         
        hbond_regex = re.compile(r'! Nr of hydrogen bonds')
    
        #Determine what lines each of these start
        general_start = 2
        self.f.seek(0)
        for i, line in enumerate(self.f):
            if atom_regex.search(line):
                atom_start = i+1 #line num = iter + 1
            elif bond_regex.search(line):
                bond_start = i+1 #line num = iter + 1
            elif offdiag_regex.search(line):
                offdiag_start = i+1 #line num = iter + 1
            elif angle_regex.search(line):
                angle_start = i+1 #line num = iter + 1
            elif torsion_regex.search(line):
                torsion_start = i+1 #line num = iter + 1
            elif hbond_regex.search(line):
                hbond_start = i+1 #line num = iter + 1
    
        #print atom_start
        #print bond_start
        #print offdiag_start
        #print angle_start
        #print torsion_start
        #print hbond_start
    
        #General section: Anything between general_start and atom_start.
        self.sections['general'] = get_lines(self.f, general_start+1, atom_start-1)
        #print sections['general'][0]
    
        #Atom section: Since each atom entry is exactly four lines, and since the
        #comment after the 'Nr atoms' specification line seems to follow this
        #convention too, we will just skip four lines after the specification line.
        self.sections['atom'] = get_lines(self.f, atom_start+4, bond_start-1)
        #print sections['atom'][0]
    
        #Bond section: Each bond entry is exactly two lines. Assuming that the
        #specification line follows same convention.
        self.sections['bond'] = get_lines(self.f, bond_start+2, offdiag_start-1)
        #print sections['bond'][0]
        
        #Off-diagonal section: 
        self.sections['offdiag'] = get_lines(self.f, offdiag_start+1, angle_start-1)
        #print sections['offdiag'][0]
    
        #Angle section: 
        self.sections['angle'] = get_lines(self.f, angle_start+1, torsion_start-1)
        #print sections['angle'][0]
        
        #Torsion section: 
        self.sections['torsion'] = get_lines(self.f, torsion_start+1, hbond_start-1)
        #print sections['torsion'][0]
        
        #Hydrogen Bond section: 
        self.sections['hbond'] = get_lines(self.f, hbond_start+1, None) #To end of file
        #print sections['hbond'][0]

    def get_atom_num_mapping(self):
        '''
        Returns a dictionary where the keys are atom labels and the values are
        the corresponding atom number (according to the how they are ordered in
        the ffield file).

        @return dict Dictionary where keys are atom labels and values are
                     corresponding atom numbers.
        '''
        atom_num_dict = {}
        
        #Sample starting line:
        # C    1.3817   4.0000  12.0000   1.8903   0.1838   0.9000   1.1341   4.0000     
        #First, get a list of all the atom labels in the order that they appear.
        start_regex = re.compile(r'^\s*([A-Za-z]+)\s+.+')
        count = 1
        for line in self.sections['atom']:
            m = start_regex.match(line)
            if m: #check if there is a match
                atom_num_dict[m.group(1)] = count
                count += 1
        
        return atom_num_dict
    
    def atom_num_lookup(self, atom_label):
        '''
        Given an array of lines for the atom section and an atom label (ie. 'C',
        'H', etc.), returns the atom number associated with that label.
    
        @param atom_label String for atom label (ie. 'C', 'H', etc.).
        @return int Integer associated with that atom label.
        '''
        atom_num_dict = self.get_atom_num_mapping()
        try:
            atom_num_dict[atom_label]
        except KeyError:
            print 'ERROR: '+atom_label+' could not be found in atoms dict.'
            sys.exit()

        return atom_num_dict[atom_label]
       

    def atom_section_to_dict(self):
        '''
        Given an array of lines for the atom section, parses the lines into a
        dictionary where each key is the atom type (ie. 'C', 'H', etc.) and the
        value are the four lines associated with each atom.
    
        @param lines Array of strings that comprise the lines of the atom section.
        @return dict Dictionary, each key is atom type; each value contains the
                     associated four lines of that atom type.
        '''
        lines = self.sections['atom']
        atom_dict = {}
        
        #Sample starting line:
        # C    1.3817   4.0000  12.0000   1.8903   0.1838   0.9000   1.1341   4.0000     
        start_regex = re.compile(r'^\s*([A-Za-z]+)\s+.+')
        for i, line in enumerate(lines):
            m = start_regex.match(line)
            if m: #check if there is a match
                entry = []
                #Add the four lines to this array
                entry.append(line)
                entry.append(lines[i+1])
                entry.append(lines[i+2])
                entry.append(lines[i+3])
                
                #Now add to dictionary
                if m.group(1) in atom_dict:
                    print 'ERROR (atom): '+m.group(1)+' already exists!'
                atom_dict[m.group(1)] = entry
    
        return atom_dict
            
    def bond_section_to_dict(self):
        '''
        Given an array of lines for the bond section, parses the lines into a
        dictionary where each key is a representation of the bond where the smaller
        atom number is always on the left (ie. '1|2', '3|5', '4|15', etc.), and the
        value are the two lines associated with each bond.
    
        @param lines Array of strings that comprise the lines of the bond section.
        @return dict Dictionary, each key is bond representation; each value is an
                     array of strings that contains the associated two lines of that
                     bond type.
        '''
        lines = self.sections['bond']
        bond_dict = {}
        
        #Sample two lines:
        #1  1 158.2004  99.1897  78.0000  -0.7738  -0.4550   1.0000  37.6117   0.4147  
        #       0.4590  -0.1000   9.1628   1.0000  -0.0777   6.7268   1.0000   0.0000  
        #To parse:
        #The number of lines in 'lines' array MUST be even since each entry has two
        #associated lines. Therefore, just skip by every two lines.
        assert len(lines) % 2 == 0 #eq 0 if even, 1 if odd
        for i in xrange(0, len(lines), 2): #skip by two
            #The first line begins with two numbers of atoms that are being bonded:
            s = lines[i].split()
            assert len(s) == 10 #sanity check
            atom1 = int(s[0])
            atom2 = int(s[1])
    
            #Now we want to make the key label. We always write the smaller atom
            #number to the left so that we don't end up with duplicates. For
            #instance, between atom 1 and 15, we always make the key as: '1|15' and
            #not as: '15|1'.
            if atom1 <= atom2:
                key = str(atom1)+'|'+str(atom2)
            else:
                key = str(atom2)+'|'+str(atom1)
    
            #Put in dictionary
            entry = []
            entry.append(lines[i])
            entry.append(lines[i+1])
            if key in bond_dict:
                print 'ERROR (bond): '+key+' already exists!'
            bond_dict[key] = entry
    
        return bond_dict
    
    def offdiag_section_to_dict(self):
        '''
        Given an array of lines for the off-diagonal section, parses the lines into a
        dictionary where each key is a representation of the off-diag where the smaller
        atom number is always on the left (ie. '1|2', '3|5', '4|15', etc.), and the
        value is the line associated with each off-diagonal term.
    
        @param lines Array of strings that comprise the lines of the off-diag section.
        @return dict Dictionary, each key is off-diag representation; each value
                     is a string that contains the associated line of that bond type.
        '''
        lines = self.sections['offdiag']
        offdiag_dict = {}
        
        #Sample line:
        #  1  2   0.1239   1.4004   9.8467   1.1210  -1.0000  -1.0000                    
        for line in lines:
            #The line begins with two numbers of atoms in the off-diag:
            s = line.split()
            assert len(s) == 8 #sanity check
            atom1 = int(s[0])
            atom2 = int(s[1])
    
            #Now we want to make the key label. We always write the smaller atom
            #number to the left so that we don't end up with duplicates. For
            #instance, between atom 1 and 15, we always make the key as: '1|15' and
            #not as: '15|1'.
            if atom1 <= atom2:
                key = str(atom1)+'|'+str(atom2)
            else:
                key = str(atom2)+'|'+str(atom1)
    
            #Put in dictionary
            if key in offdiag_dict:
                print 'ERROR (offdiag): '+key+' already exists!'
            offdiag_dict[key] = line
    
        return offdiag_dict
    
    def angle_section_to_dict(self):
        '''
        Given an array of lines for the angle section, parses the lines into a
        dictionary where each key is a representation of the angle where the left-
        most number is always smaller than the right-most number (ie. '1|5|2',
        '3|4|5', '4|1|15', etc.), and the value is the line associated with each
        angle term.
    
        @param lines Array of strings that comprise the lines of the angle section.
        @return dict Dictionary, each key is angle representation; each value
                     is a string that contains the associated line of that angle.
        '''
        lines = self.sections['angle']
        angle_dict = {}
        
        #Sample line:
        #  1  1  1  59.0573  30.7029   0.7606   0.0000   0.7180   6.2933   1.1244        
        for line in lines:
            #The line begins with three numbers denoting the atoms involved in
            #angle:
            s = line.split()
            assert len(s) == 10 #sanity check
            atom1 = int(s[0])
            atom2 = int(s[1])
            atom3 = int(s[2])
    
            #Now we want to make the key label. We know that an angle representation
            #like:  1 2 3 is equivalent to 3 2 1. Essentially, the middle term must
            #remain in place, but the end terms can swap. Therefore, for consistency
            #in comparison, we always write the smaller atom number of the two ends
            #on the left end. For example, 6 1 4 would be written as '4|1|6'.
            if atom1 <= atom3:
                key = str(atom1)+'|'+str(atom2)+'|'+str(atom3)
            else:
                key = str(atom3)+'|'+str(atom2)+'|'+str(atom1)
    
            #Put in dictionary
            if key in angle_dict:
                print 'ERROR (angle): '+key+' already exists!'
            angle_dict[key] = line
    
        return angle_dict
    
    def torsion_section_to_dict(self):
        '''
        Given an array of lines for the torsion section, parses the lines into a
        dictionary where each key is a representation of the torsion where the
        left-most number is always smaller than the right-most number (ie.
        '1|5|3|2', '3|4|8|5', '4|19|2|15', etc.), and the value is the line
        associated with each torsion term.
    
        @param lines Array of strings that comprise the lines of the torsion section.
        @return dict Dictionary, each key is torsion representation; each value
                     is a string that contains the associated line of that torsion.
        '''
        lines = self.sections['torsion']
        torsion_dict = {}
        
        #Sample line:
        #  1  1  1  1  -0.2500  34.7453   0.0288  -6.3507  -1.6000   0.0000   0.0000     
        for line in lines:
            #The line begins with four numbers denoting the atoms involved in
            #torsion:
            s = line.split()
            assert len(s) == 11 #sanity check
            atom1 = int(s[0])
            atom2 = int(s[1])
            atom3 = int(s[2])
            atom4 = int(s[3])
    
            #Now we want to make the key label. We know that an torsion representation
            #like:  1 2 3 4 is equivalent to 4 3 2 1. Essentially, the order
            #matters, but the sequence can be flipped/reversed. Therefore, for
            #consistency in comparison, we always write the smaller atom number of
            #the two ends on the left end. For example, 6 1 4 3 would be written as
            #'3|4|1|6'.
            if atom1 <= atom4:
                key = str(atom1)+'|'+str(atom2)+'|'+str(atom3)+'|'+str(atom4)
            else:
                key = str(atom4)+'|'+str(atom3)+'|'+str(atom2)+'|'+str(atom1)
    
            #Put in dictionary
            if key in torsion_dict:
                print 'ERROR (torsion): '+key+' already exists!'
            torsion_dict[key] = line
    
        return torsion_dict
    
    def hbond_section_to_dict(self):
        '''
        Given an array of lines for the hbond section, parses the lines into a
        dictionary where each key is a representation of the hbond (order of the
        atom numbers matter), and the value is the line associated with each hbond
        term.
    
        @param lines Array of strings that comprise the lines of the hbond section.
        @return dict Dictionary, each key is hbond representation; each value
                     is a string that contains the associated line of that hbond.
        '''
        lines = self.sections['hbond']
        hbond_dict = {}
        
        #Sample line:
        #  3  2  3   2.1200  -3.5800   1.4500  19.5000                                   
        for line in lines:
            #The line begins with three numbers denoting the atoms involved in
            #angle:
            s = line.split()
            assert len(s) == 7 #sanity check
            atom1 = int(s[0])
            atom2 = int(s[1])
            atom3 = int(s[2])
    
            #Now we want to make the key label. The order of the atom number is
            #important so we create the key label according to the order specified.
            key = str(atom1)+'|'+str(atom2)+'|'+str(atom3)
    
            #Put in dictionary
            if key in hbond_dict:
                print 'ERROR (hbond): '+key+' already exists!'
            hbond_dict[key] = line
    
        return hbond_dict
    
    


def tests():
    
    print 'All tests completed successfully!'
    sys.exit(0)



def main():
    print 'here'
    to_ffield   = 'ffield_ti-o-h-na-cl-s-p'
    to_f = Ffield()
    to_f.load(to_ffield)
    to_f.parse_sections()
    to_atom_dict = to_f.atom_section_to_dict()
    to_bond_dict = to_f.bond_section_to_dict()
    to_offdiag_dict = to_f.offdiag_section_to_dict()
    to_angle_dict = to_f.angle_section_to_dict()
    to_torsion_dict = to_f.torsion_section_to_dict()
    to_hbond_dict = to_f.hbond_section_to_dict()
    
    #tests()
    pass

if __name__ == '__main__':
    main()

