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
#import os #For file exist check and splitext and path stuff
import re
#import time #for sleep
import itertools

from ffield import Ffield

from_ffield = 'ffield_v-bi-ti-mo-ruN'
to_ffield   = 'ffield_ti-o-h-na-cl-s-p'
#to_ffield = 'ffield_v-bi-ti-mo-ruN'
#from_ffield   = 'ffield_ti-o-h-na-cl-s-p'
#move_atoms = ('C', 'H', 'O', 'N', 'S')
#move_atoms = ('Ti',)
move_atoms = ('Ru',)


def main():
    merged_sections = {}

    #Parse file into each section
    from_f = Ffield()
    from_f.load(from_ffield)
    from_f.parse_sections()
    #from_atom_dict = from_f.atom_section_to_dict()
    #print from_atom_dict.keys()
    #from_bond_dict = from_f.bond_section_to_dict()
    #from_offdiag_dict = from_f.offdiag_section_to_dict()
    #from_angle_dict = from_f.angle_section_to_dict()
    #from_torsion_dict = from_f.torsion_section_to_dict()
    #from_hbond_dict = from_f.hbond_section_to_dict()
    
    to_f = Ffield()
    to_f.load(to_ffield)
    to_f.parse_sections()
    #to_atom_dict = to_f.atom_section_to_dict()
    #print to_atom_dict.keys()
    #to_bond_dict = to_f.bond_section_to_dict()
    #to_offdiag_dict = to_f.offdiag_section_to_dict()
    #to_angle_dict = to_f.angle_section_to_dict()
    #to_torsion_dict = to_f.torsion_section_to_dict()
    #to_hbond_dict = to_f.hbond_section_to_dict()
    
    #Now create merged sections. Merge moves entries from 'from'
    #to 'to' that are specified in the move_atoms tuple despite any conflict.
    #The 'from' version will overwrite the 'to' version.
    merge_f = Ffield_merge()
    merge_f.from_f = from_f
    merge_f.to_f = to_f
    merge_f.move_atoms = move_atoms
    merged_atom_dict = merge_f.merge_atom_dict()
    #print merged_atom_dict.keys()
    
    #Save merged atom section to the 'to' ffield. (Easier than creating a whole
    #new merged ffield file for now).
    #TODO: Have atom_dict_to_lines call merge_atom_dict() without needing the
    #      user to pass in the merged atom dict.
    merged_sections['atom'] = merge_f.atom_dict_to_lines(merged_atom_dict)
    to_f.sections['atom'] = merged_sections['atom']
    #print merged_sections['atom']
    #print to_f.sections['atom']
    #print from_f.get_atom_num_mapping()
    #print to_f.get_atom_num_mapping()
    #print merge_f.to_f.get_atom_num_mapping()
   
    #Get the equivalent numbers of our move_atoms. We do this after we've merged
    #the atom_dicts so that the atoms we moved over will exist in our 'to' map.
    #from_move_atoms_num = []
    #to_move_atoms_num = []
    #for atom_label in move_atoms:
    #    from_move_atoms_num.append(from_f.atom_num_lookup(atom_label))
    #    to_move_atoms_num.append(to_f.atom_num_lookup(atom_label))
    #from_move_atoms_num = tuple(from_move_atoms_num)
    #to_move_atoms_num = tuple(to_move_atoms_num)
    #move_atoms_num = {'from': from_move_atoms_num, 'to': to_move_atoms_num}
    #print move_atoms_num

    merged_bond_dict = merge_f.merge_bond_dict()
    #merged_bond_dict = merge_bond_dict(from_bond_dict, to_bond_dict,
    #                                   move_atoms_num)
    #print merged_bond_dict
    
    return

    ##Parse text into dict-line
    #base_dict = text_to_dict(base_text.splitlines())
    ##print str(len(base_dict))
    #override_dict = text_to_dict(override_text.splitlines())

    ##Merge dicts
    #merged_dict = merge_dicts(base_dict, override_dict)

    ##Now print out all lines:
    #for k, v in merged_dict.iteritems():
    #    print v
    #
    #print 'Total entries: '+str(len(merged_dict))

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

        #NOTE: Instead of creating a separate merge_dict, we will just make all the
        #      changes on to_dict.
        for k, v in from_dict.iteritems():
            #Deconstruct the key into atom numbers:
            #TODO: move this into ffield class.
            from_atoms_in_bond = k.split('|')
            from_atoms_in_bond = map(int, from_atoms_in_bond) #Convert str to int
            from_atoms_in_bond = set(from_atoms_in_bond)

            #Since we will only work with bonds that have at least one atom from
            #move_atoms, let's weed out entries that we don't consider here.
            #The approach here is to get the union of our bond atoms and move atoms.
            #If both of our bond atoms are in move atoms set, then the len of the
            #combined set will be the same as the len of the move atoms set. If one
            #of our bond atoms are in the move atoms set, then the len will be one
            #greater than the len of the move atoms set. So to check for no match, we
            #check for unions greater than len(move_atoms_num) + 1.
            at_least_one = False
            for atom_num in from_atoms_in_bond:
                atom_label = self.from_f.atom_label_lookup(atom_num)
                if atom_label in self.move_atoms:
                    at_least_one = True
                    break
            if at_least_one == False:
                continue


            #if len(from_atoms_in_bond.union(move_atoms_num)) > \
            #    len(move_atoms_num) + 1:
            #    continue #Move on to next bond
            
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
            
            #At this point:
            #1. At least one atom in bond is in our move_atoms list.
            #2. Both atoms in bond are in the 'to' atoms list.
            #So, let's move the bond entry in 'from' to 'to'. But first, need to
            #modify the 'from' entry to reflect the new atom numbers.
            def replace_bond(line, old_num, new_num):
                old_num = str(old_num)
                new_num = str(new_num)

                r = re.compile(r' '+old_num+' ')
                #Determine if old_num and new_num has the same number of digits.
                #If new_num has one less digit, then insert an extra space
                #before the replacement. If one more digit, then remove an space
                #before the replacement.
                #print new_num
                #print old_num
                if len(new_num) < len(old_num):
                    #Currently, assume one digit difference:
                    repl = '  '+new_num+' '
                elif len(new_num) > len(old_num):
                    repl = ''+new_num+' '
                else:
                    repl = ' '+new_num+' '

                return r.sub(repl, line)

            for old_num, new_num in zip(from_atoms_in_bond,
                                        equiv_to_atoms_in_bond):
                #DANGER! There could be a case, where the second replacement
                #overwrites the first replacement. Ie. If first replacement
                #results in replacing 5 with 9, but the second replacement
                #replaces 9 with 13.
                v[0] = replace_bond(v[0], old_num, new_num)  #First line
            
            print 'Merged '+k
            print v
            merge_dict[k] = v
    
        return merge_dict
    
    #def get_equivalent_atom_num(from_atoms, to_atoms, from_atom_num):
    #    '''
    #    Given a list/tuple of from_atoms and to_atoms and also an atom number from
    #    the from_atom list, returns the equivalent atom number from the to_atoms
    #    list.
    #
    #    @param from_atoms List/tuple of atom numbers.
    #    @param to_atoms List/tuple of atom numbers that has equivalent ordering as
    #                    the from_atoms list.
    #    @param from_atom_num An atom number from the from_atoms list that we are
    #                         trying to convert to a 'to' atom number.
    #    @return int Equivalent atom num that is in the 'to_atoms' list.
    #    '''
    #    from_atoms = list(from_atoms) #Must be list to use .index() method
    #    
    #    try:
    #        i = from_atoms.index(from_atom_num)
    #    except ValueError:
    #        print 'ERROR: Atom number '+str(from_atom_num)+" does not "+\
    #              "exist in 'from' list"
    #        sys.exit()
    #
    #    try:
    #        to_atoms[i]
    #    except IndexError:
    #        print 'ERROR: Index '+str(i)+" does not "+\
    #              "exist in 'to' list"
    #        sys.exit()
    #
    #
    #    return to_atoms[i]




def text_to_dict(text):
    dict = {}
    for line in text:
        line_elements = line.split() #splits by space
        if len(line_elements) > 1:
            #Combine first four to make key
            k = ''.join(line_elements[0:4])
            if k in dict:
                print 'ERROR: '+k+' already exists!'
            dict[k] = line
            #print dict[k]
        #else:
        #    print 'ERROR: '+line

    return dict


def tests():

    print 'All tests completed successfully!'
    sys.exit(0)


if __name__ == '__main__':
    #tests()
    main()
