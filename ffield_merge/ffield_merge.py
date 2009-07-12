#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
ffield_merge.py
-----------------
Merges two torsions part of a ffield file.
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import sys #For arguments and exit (in older python versions)
import re
import itertools

from ffield import Ffield

#Arguments. Set some defaults before the control file in case the user does not
#define them.
overwrite = True
merge_only_conflicts = False
only_merge_specified_atoms = False
try:
    control_file= sys.argv[1] #Settings for RDF
except IndexError:
    print 'Usage: ffield_merge [controlfile]'
    print 'Since no control file specified, assuming the file is: control'
    control_file = 'control'

#Source the control file:
try:
    execfile(control_file)
except IOError: 
    print 'Error: '+control_file+' does not exist!'
    sys.exit(1)
print 'Read control file successfully: '+control_file


def main():
    #Parse file into each section
    from_f = Ffield()
    from_f.load(from_ffield)
    from_f.parse_sections()
    
    to_f = Ffield()
    to_f.load(to_ffield)
    to_f.parse_sections()
    
    #Now create merged sections. Merge moves entries from 'from'
    #to 'to' that are specified in the move_atoms tuple despite any conflict.
    #The 'from' version will overwrite the 'to' version.
    merge_f = Ffield_merge()
    merge_f.from_f = from_f
    merge_f.to_f = to_f
    merge_f.move_atoms = move_atoms
    
    #Save merged atom section to the 'to' ffield. (Easier than creating a whole
    #new merged ffield file for now).
    #TODO: Have atom_dict_to_lines call merge_atom_dict() without needing the
    #      user to pass in the merged atom dict.
    if 'atom' in merge_sections:
        merged_atom_dict = merge_f.merge_atom_dict()
        to_f.sections['atom'] = merge_f.atom_dict_to_lines(merged_atom_dict)

    if 'bond' in merge_sections:
        merged_bond_dict = merge_f.merge_bond_dict()
        to_f.sections['bond'] = merge_f.generic_dict_to_lines(merged_bond_dict)
    
    if 'offdiag' in merge_sections:
        merged_offdiag_dict = merge_f.merge_offdiag_dict()
        to_f.sections['offdiag'] = merge_f.generic_dict_to_lines(merged_offdiag_dict)
    
    if 'angle' in merge_sections:
        merged_angle_dict = merge_f.merge_angle_dict()
        to_f.sections['angle'] = merge_f.generic_dict_to_lines(merged_angle_dict)
    
    if 'torsion' in merge_sections:
        merged_torsion_dict = merge_f.merge_torsion_dict()
        to_f.sections['torsion'] = merge_f.generic_dict_to_lines(merged_torsion_dict)

    if 'hbond' in merge_sections:
        merged_hbond_dict = merge_f.merge_hbond_dict()
        to_f.sections['hbond'] = merge_f.generic_dict_to_lines(merged_hbond_dict)

    #Now save everything to a new file:
    print 'Saved merged ffield file to: '+merged_ffield
    to_f.save(merged_ffield)

class Ffield_merge:
    from_f = None
    to_f = None
    move_atoms = ()
    
    def get_equivalent_to_atom_num(self, from_atom_num):
        '''
        Given an atom num from 'from' ffield, returns the equivalent atom num
        from the 'to' ffield. If no equivalent atom num exists, raises
        ValueError.
        '''
        #Look up label for the given 'from' atom num:
        try:
            from_atom_label = self.from_f.atom_label_lookup(from_atom_num)
        except ValueError:
            #Means that the atom num was not found.
            print 'ERROR: Atom num '+from_atom_num+" was not found in the "+\
                  +'from ffield!'
            sys.exit(0)
        
        #Now find the number in 'to' for this label:
        try:
            to_atom_num = self.to_f.atom_num_lookup(from_atom_label)
        except ValueError:
            #Means that the atom label was not found.
            raise ValueError
            #return False

        return to_atom_num
    
    def atom_dict_to_lines(self, atom_dict):
        '''
        Given an atom dict, will return a list of strings that
        comprise the atom section of ffield structured in a way such that new
        entries are placed after existing entries of the 'to' ffield object.
        TODO: Place new entries before the 'X' atom be after existing entries.
        
        @param atom_dict Atoms dictionary that we want to add to the ffield object.
        @return list List of strings that represents the atom section of ffield.
        '''
        #Get a mapping of atom label to num for existing entries so that we know
        #what the order should be.
        atom_num_map = self.to_f.get_atom_num_mapping()
        
        #Now generate an array of atom labels that denotes the order which we will
        #output the existing entries.
        num_atoms = len(atom_num_map)
        atoms_label_order = []
        #Helper function:
        def get_atom_label_for_num(num):
            for k, v in atom_num_map.iteritems():
                if v == num:
                    return k
        for i in range(1, num_atoms+1): #generates numbers 1 to num_atoms
            atoms_label_order.append(get_atom_label_for_num(i))
    
        #Now do we have new entries? We generate a new set composed of elements in
        #current_labels that are not in existing_labels:
        existing_labels = set(atom_num_map.keys())
        current_labels = set(atom_dict.keys())
        new_labels = current_labels.difference(existing_labels)
        #Now add to our atom labels order list. If new_labels is empty, nothing
        #happens.
        atoms_label_order.extend(new_labels)
    
        #Now generate our output list:
        output = []
        for k in atoms_label_order:
            #Atom entries are 4 lines long, so we must keep that in mind when
            #appending:
            for line in atom_dict[k]:
                output.append(line)
    
        return output
    
    def merge_atom_dict(self):
        '''
        Given two atom dicts (from and to) and atoms to forcefully
        move over (the specified 'from' atoms will overwrite the 'to' atoms), will
        return a dictionary with merged atom entries.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.atom_section_to_dict()
        to_dict = self.to_f.atom_section_to_dict()
        merge_dict = to_dict.copy()
        for k, v in from_dict.iteritems():
            #If there is no conflict in merger, or if move_atoms say that we must
            #move the atom_label entry:
            if k in self.move_atoms:
                #Check if we overwrote an existing entry (for informative purposes):
                if k in to_dict:
                    print 'Merged '+k+' but overwrote existing entry.'
                else:
                    print 'Merged '+k
    
                merge_dict[k] = v
    
        return merge_dict
    
    def merge_bond_dict(self):
        '''
        Given two bond dicts (from and to) and also optional atoms to forcefully
        move over (the specified from atoms will overwrite the to atoms), will
        return a dictionary with merged bond entries. For a bond entry to be
        forcefully copied over (possibly replacing any such existing entries in
        'to_dict'), at least one atoms involved in the bond must be specified in the
        move_atoms list.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.bond_section_to_dict()
        to_dict = self.to_f.bond_section_to_dict()
        merge_dict = to_dict.copy()

        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_bond = k.split('|')
            from_atoms_in_bond = map(int, from_atoms_in_bond) #Convert str to int
            #NOTE: Don't make from_atoms_in_bond into a set() since bond entries
            #can be two atoms of the same number, which sets cannot handle.

            if only_merge_specified_atoms == True:
                #Then all atoms MUST be in the move_atoms list.
                from_atoms_in_bond_set = set(from_atoms_in_bond)
                if not from_atoms_in_bond_set.issubset(self.move_atoms):
                    continue
            
            #Since we will only work with bonds that have at least one atom from
            #move_atoms, let's weed out entries that we don't consider here.
            at_least_one = False
            for atom_num in from_atoms_in_bond:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue

            #Now convert the atom numbers from 'from' to the equivalent atom numbers
            #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
            #we make that conversion here (using list comprehension). 
            #Also, all atoms in bond MUST be in the atoms list for the 'to'
            #file. Otherwise, there's no point in moving it over since it won't
            #be used anyway.
            try:
                equiv_to_atoms_in_bond = [self.get_equivalent_to_atom_num(i) \
                                          for i in from_atoms_in_bond]
            except ValueError:
                #Means that at least one of the atoms do not exist in the 'to'
                #file.
                continue #Move to next bond
            
            if overwrite == False: #Means we do not overwrite on conflicts
                if k in merge_dict:
                    print 'Conflict, so skipping: '+k
                    continue #Move to next entry

            if merge_only_conflicts == True:
                if k not in merge_dict:
                    print 'No conflict, so skipping: '+k
                    continue
            
            #At this point:
            #1. At least one atom in bond is in our move_atoms list.
            #2. Both atoms in bond are in the 'to' atoms list.
            #So, let's move the bond entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def generate_atom_num_string(atoms):
                '''
                Given atom numbers in a tuple, generates a string of those atom
                numbers.
                '''
                atom_num_str = ' ' #Start with a space
                for atom in atoms:
                    #atom will be at most two digits. If one digit, we want the
                    #ten's digit place to be a space:
                    atom_num_str += '%2d ' % atom
                return atom_num_str

            #Generate atoms num string
            for z in range(2): #z is not used, loop used to count twice
                pattern = generate_atom_num_string(from_atoms_in_bond)
                repl = generate_atom_num_string(equiv_to_atoms_in_bond)
                s = re.subn(pattern, repl, v[0])
                if s[1] <= 0: 
                    #If no substitutions were made, this is most likely that the
                    #entry in the file has the bonds reversed (ie. Instead of 1 2
                    #it's 2 1). Therefore, we will reverse the order here and try
                    #to re-replace.
                    print 'Failed to merged (bond) '+k+' to '+str(equiv_to_atoms_in_bond)
                    print 'Reversing the order and trying again...'
                    from_atoms_in_bond = list(from_atoms_in_bond)
                    from_atoms_in_bond.reverse()
                    equiv_to_atoms_in_bond = list(equiv_to_atoms_in_bond)
                    equiv_to_atoms_in_bond.reverse()
                    continue #Retry the substitution
            if s[1] <= 0: 
                print 'ERROR: Bond substitution failed!'
                raise Exception
            
            v[0] = s[0] #Holds the substituted string
            print 'Merged (bond) '+k+' to '+str(equiv_to_atoms_in_bond)
            #print v
            merge_dict[k] = v
    
        return merge_dict
    
    def merge_offdiag_dict(self):
        '''
        Given two offdiag dicts (from and to) and also optional atoms to forcefully
        move over (the specified from atoms will overwrite the to atoms), will
        return a dictionary with merged offdiag entries. For an offdiag entry to be
        forcefully copied over (possibly replacing any such existing entries in
        'to_dict'), at least one atoms involved in the offdiag must be specified
        in the move_atoms list.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.offdiag_section_to_dict()
        to_dict = self.to_f.offdiag_section_to_dict()
        merge_dict = to_dict.copy()

        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_offdiag = k.split('|')
            from_atoms_in_offdiag = map(int, from_atoms_in_offdiag) #Convert str to int

            if only_merge_specified_atoms == True:
                #Then all atoms MUST be in the move_atoms list.
                from_atoms_in_bond_set = set(from_atoms_in_bond)
                if not from_atoms_in_bond_set.issubset(self.move_atoms):
                    continue
            
            #Since we will only work with offdiag entries that have at least one
            #atom from move_atoms, let's weed out entries that we don't consider
            #here.  
            at_least_one = False
            for atom_num in from_atoms_in_offdiag:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue

            #Now convert the atom numbers from 'from' to the equivalent atom numbers
            #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
            #we make that conversion here (using list comprehension). 
            #Also, all atoms in bond MUST be in the atoms list for the 'to'
            #file. Otherwise, there's no point in moving it over since it won't
            #be used anyway.
            try:
                equiv_to_atoms_in_offdiag = [self.get_equivalent_to_atom_num(i) \
                                             for i in from_atoms_in_offdiag]
            except ValueError:
                #Means that at least one of the atoms do not exist in the 'to'
                #file.
                continue #Move to next offdiag
            
            if overwrite == False: #Means we do not overwrite on conflicts
                if k in merge_dict:
                    print 'Conflict, so skipping: '+k
                    continue #Move to next entry
            
            if merge_only_conflicts == True:
                if k not in merge_dict:
                    print 'No conflict, so skipping: '+k
                    continue
            
            #At this point:
            #1. At least one atom in offdiag is in our move_atoms list.
            #2. Both atoms in offdiag are in the 'to' atoms list.
            #So, let's move the offdiag entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def generate_atom_num_string(atoms):
                '''
                Given atom numbers in a tuple, generates a string of those atom
                numbers.
                '''
                atom_num_str = ' ' #Start with a space
                for atom in atoms:
                    #atom will be at most two digits. If one digit, we want the
                    #ten's digit place to be a space:
                    atom_num_str += '%2d ' % atom
                return atom_num_str

            #Generate atoms num string
            for z in range(2): #z is not used, loop used to count twice
                pattern = generate_atom_num_string(from_atoms_in_offdiag)
                repl = generate_atom_num_string(equiv_to_atoms_in_offdiag)
                s = re.subn(pattern, repl, v)
                if s[1] <= 0: 
                    #If no substitutions were made, this is most likely that the
                    #entry in the file has the bonds reversed (ie. Instead of 1 2
                    #it's 2 1). Therefore, we will reverse the order here and try
                    #to re-replace.
                    print 'Failed to merged (offdiag) '+k+' to '+str(equiv_to_atoms_in_offdiag)
                    print 'Reversing the order and trying again...'
                    from_atoms_in_offdiag = list(from_atoms_in_offdiag)
                    from_atoms_in_offdiag.reverse()
                    equiv_to_atoms_in_offdiag = list(equiv_to_atoms_in_offdiag)
                    equiv_to_atoms_in_offdiag.reverse()
                    continue #Retry the substitution
            if s[1] <= 0: #If no substitutions were made
                print 'ERROR: Offdiag substitution failed!'
                raise Exception
            
            v = s[0] #Holds the substituted string
            print 'Merged (offdiag) '+k+' to '+str(equiv_to_atoms_in_offdiag)
            #print v
            merge_dict[k] = v
    
        return merge_dict
    
    def generic_dict_to_lines(self, dict):
        '''
        Given a dict, will return a list of strings that comprise the
        section of ffield. 
        
        @param dict Dictionary that we want to add to the ffield object.
        @return list List of strings that represents the atom section of ffield.
        '''
        #The good thing is that when we merged entries, we already updated the
        #merged bond numbers to reflect any merged atom entries. So essentially,
        #we can just generate the output without modification:
        output = []
        for k, v in dict.iteritems():
            #This is to take into account when entries are more than one line:
            if type(v) == type([]):
                for line in v:
                    output.append(line)
            else:
                output.append(v)
    
        return output
    
    def merge_angle_dict(self):
        '''
        Given two angle dicts (from and to) and also optional atoms to forcefully
        move over (the specified from atoms will overwrite the to atoms), will
        return a dictionary with merged angle entries. For an angle entry to be
        forcefully copied over (possibly replacing any such existing entries in
        'to_dict'), at least one atoms involved in the angle must be specified
        in the move_atoms list.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.angle_section_to_dict()
        to_dict = self.to_f.angle_section_to_dict()
        merge_dict = to_dict.copy()

        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_angle = k.split('|')
            from_atoms_in_angle = map(int, from_atoms_in_angle) #Convert str to int

            if only_merge_specified_atoms == True:
                #Then all atoms MUST be in the move_atoms list.
                from_atoms_in_bond_set = set(from_atoms_in_bond)
                if not from_atoms_in_bond_set.issubset(self.move_atoms):
                    continue
            
            #Since we will only work with angle entries that have at least one
            #atom from move_atoms, let's weed out entries that we don't consider
            #here.  
            at_least_one = False
            for atom_num in from_atoms_in_angle:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue

            #Now convert the atom numbers from 'from' to the equivalent atom numbers
            #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
            #we make that conversion here (using list comprehension). 
            #Also, all atoms in bond MUST be in the atoms list for the 'to'
            #file. Otherwise, there's no point in moving it over since it won't
            #be used anyway.
            try:
                equiv_to_atoms_in_angle = [self.get_equivalent_to_atom_num(i) \
                                           for i in from_atoms_in_angle]
            except ValueError:
                #Means that at least one of the atoms do not exist in the 'to'
                #file.
                continue #Move to next offdiag
            
            if overwrite == False: #Means we do not overwrite on conflicts
                if k in merge_dict:
                    print 'Conflict, so skipping: '+k
                    continue #Move to next entry
            
            if merge_only_conflicts == True:
                if k not in merge_dict:
                    print 'No conflict, so skipping: '+k
                    continue
            
            #At this point:
            #1. At least one atom in offdiag is in our move_atoms list.
            #2. Both atoms in offdiag are in the 'to' atoms list.
            #So, let's move the offdiag entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def generate_atom_num_string(atoms):
                '''
                Given atom numbers in a tuple, generates a string of those atom
                numbers.
                '''
                atom_num_str = ' ' #Start with a space
                for atom in atoms:
                    #atom will be at most two digits. If one digit, we want the
                    #ten's digit place to be a space:
                    atom_num_str += '%2d ' % atom
                return atom_num_str

            #Generate atoms num string
            for z in range(2): #z is not used, loop used to count twice
                pattern = generate_atom_num_string(from_atoms_in_angle)
                repl = generate_atom_num_string(equiv_to_atoms_in_angle)
                s = re.subn(pattern, repl, v)
                if s[1] <= 0: 
                    #If no substitutions were made, this is most likely that the
                    #entry in the file has the bonds reversed (ie. Instead of 1 2
                    #it's 2 1). Therefore, we will reverse the order here and try
                    #to re-replace.
                    print 'Failed to merge (angle) '+k+' to '+str(equiv_to_atoms_in_angle)
                    print 'Reversing the order and trying again...'
                    from_atoms_in_angle = list(from_atoms_in_angle)
                    from_atoms_in_angle.reverse()
                    equiv_to_atoms_in_angle = list(equiv_to_atoms_in_angle)
                    equiv_to_atoms_in_angle.reverse()
                    continue #Retry the substitution
            if s[1] <= 0: #If no substitutions were made
                print 'ERROR: Angle substitution failed!'
                raise Exception
            
            v = s[0] #Holds the substituted string
            print 'Merged (angle) '+k+' to '+str(equiv_to_atoms_in_angle)
            #print v
            merge_dict[k] = v
    
        return merge_dict
    
    def merge_torsion_dict(self):
        '''
        Given two torsion dicts (from and to) and also optional atoms to
        forcefully move over (the specified from atoms will overwrite the to
        atoms), will return a dictionary with merged torsion entries. For an
        torsion entry to be forcefully copied over (possibly replacing any such
        existing entries in 'to_dict'), at least one atoms involved in the
        torsion must be specified in the move_atoms list.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.torsion_section_to_dict()
        to_dict = self.to_f.torsion_section_to_dict()
        merge_dict = to_dict.copy()

        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_torsion = k.split('|')
            from_atoms_in_torsion = map(int, from_atoms_in_torsion) #Convert str to int
            
            if only_merge_specified_atoms == True:
                #Then all atoms MUST be in the move_atoms list.
                from_atoms_in_bond_set = set(from_atoms_in_bond)
                if not from_atoms_in_bond_set.issubset(self.move_atoms):
                    continue
            
            #Since we will only work with torsion entries that have at least one
            #atom from move_atoms, let's weed out entries that we don't consider
            #here.  
            at_least_one = False
            for atom_num in from_atoms_in_torsion:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue
            
            #Now convert the atom numbers from 'from' to the equivalent atom numbers
            #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
            #we make that conversion here (using list comprehension). 
            #Also, all atoms in bond MUST be in the atoms list for the 'to'
            #file. Otherwise, there's no point in moving it over since it won't
            #be used anyway.
            try:
                equiv_to_atoms_in_torsion = [self.get_equivalent_to_atom_num(i) \
                                           for i in from_atoms_in_torsion]
            except ValueError:
                #Means that at least one of the atoms do not exist in the 'to'
                #file.
                continue #Move to next offdiag
            
            if overwrite == False: #Means we do not overwrite on conflicts
                if k in merge_dict:
                    print 'Conflict, so skipping: '+k
                    continue #Move to next entry
            
            if merge_only_conflicts == True:
                if k not in merge_dict:
                    print 'No conflict, so skipping: '+k
                    continue
            
            #At this point:
            #1. At least one atom in torsion is in our move_atoms list.
            #2. All atoms in torsion are in the 'to' atoms list.
            #So, let's move the torsion entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def generate_atom_num_string(atoms):
                '''
                Given atom numbers in a tuple, generates a string of those atom
                numbers.
                '''
                atom_num_str = ' ' #Start with a space
                for atom in atoms:
                    #atom will be at most two digits. If one digit, we want the
                    #ten's digit place to be a space:
                    atom_num_str += '%2d ' % atom
                return atom_num_str

            #Generate atoms num string
            for z in range(2): #z is not used, loop used to count twice
                pattern = generate_atom_num_string(from_atoms_in_torsion)
                repl = generate_atom_num_string(equiv_to_atoms_in_torsion)
                s = re.subn(pattern, repl, v)
                if s[1] <= 0: 
                    #If no substitutions were made, this is most likely that the
                    #entry in the file has the bonds reversed (ie. Instead of 1 2
                    #it's 2 1). Therefore, we will reverse the order here and try
                    #to re-replace.
                    print 'Failed to merge (torsion) '+k+' to '+str(equiv_to_atoms_in_torsion)
                    print 'Reversing the order and trying again...'
                    from_atoms_in_torsion = list(from_atoms_in_torsion)
                    from_atoms_in_torsion.reverse()
                    equiv_to_atoms_in_torsion = list(equiv_to_atoms_in_torsion)
                    equiv_to_atoms_in_torsion.reverse()
                    continue #Retry the substitution
            if s[1] <= 0: #If no substitutions were made
                print 'ERROR: Torsion substitution failed!'
                raise Exception
            
            v = s[0] #Holds the substituted string
            print 'Merged (torsion) '+k+' to '+str(equiv_to_atoms_in_torsion)
            #print v
            merge_dict[k] = v
    
        return merge_dict
    
    def merge_hbond_dict(self):
        '''
        Given two hbond dicts (from and to) and also optional atoms to forcefully
        move over (the specified from atoms will overwrite the to atoms), will
        return a dictionary with merged hbond entries. For an hbond entry to be
        forcefully copied over (possibly replacing any such existing entries in
        'to_dict'), at least one atoms involved in the hbond must be specified
        in the move_atoms list.
    
        @return dict Merged dictionary from from_dict and to_dict.
        '''
        from_dict = self.from_f.hbond_section_to_dict()
        to_dict = self.to_f.hbond_section_to_dict()
        merge_dict = to_dict.copy()

        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_hbond = k.split('|')
            from_atoms_in_hbond = map(int, from_atoms_in_hbond) #Convert str to int

            if only_merge_specified_atoms == True:
                #Then all atoms MUST be in the move_atoms list.
                from_atoms_in_bond_set = set(from_atoms_in_bond)
                if not from_atoms_in_bond_set.issubset(self.move_atoms):
                    continue
            
            #Since we will only work with hbond entries that have at least one
            #atom from move_atoms, let's weed out entries that we don't consider
            #here.  
            at_least_one = False
            for atom_num in from_atoms_in_hbond:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue

            #Now convert the atom numbers from 'from' to the equivalent atom numbers
            #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
            #we make that conversion here (using list comprehension). 
            #Also, all atoms in bond MUST be in the atoms list for the 'to'
            #file. Otherwise, there's no point in moving it over since it won't
            #be used anyway.
            try:
                equiv_to_atoms_in_hbond = [self.get_equivalent_to_atom_num(i) \
                                             for i in from_atoms_in_hbond]
            except ValueError:
                #Means that at least one of the atoms do not exist in the 'to'
                #file.
                continue #Move to next hbond
            
            if overwrite == False: #Means we do not overwrite on conflicts
                if k in merge_dict:
                    print 'Conflict, so skipping: '+k
                    continue #Move to next entry
            
            if merge_only_conflicts == True:
                if k not in merge_dict:
                    print 'No conflict, so skipping: '+k
                    continue
            
            #At this point:
            #1. At least one atom in hbond is in our move_atoms list.
            #2. Both atoms in hbond are in the 'to' atoms list.
            #So, let's move the hbond entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def generate_atom_num_string(atoms):
                '''
                Given atom numbers in a tuple, generates a string of those atom
                numbers.
                '''
                atom_num_str = ' ' #Start with a space
                for atom in atoms:
                    #atom will be at most two digits. If one digit, we want the
                    #ten's digit place to be a space:
                    atom_num_str += '%2d ' % atom
                return atom_num_str

            #Generate atoms num string. The order of hbond entries is important,
            #so we don't check for any reverse cases here:
            pattern = generate_atom_num_string(from_atoms_in_hbond)
            repl = generate_atom_num_string(equiv_to_atoms_in_hbond)
            s = re.subn(pattern, repl, v)
            if s[1] <= 0: #If no substitutions were made
                print 'ERROR: Hbond substitution failed!'
                raise Exception
            
            v = s[0] #Holds the substituted string
            print 'Merged (hbond) '+k+' to '+str(equiv_to_atoms_in_hbond)
            #print v
            merge_dict[k] = v
    
        return merge_dict

def tests():

    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
