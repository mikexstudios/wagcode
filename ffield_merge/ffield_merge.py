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
move_atoms = ('C', 'H', 'O', 'N', 'S')
#move_atoms = ('Ti',)


def main():
    #Parse file into each section
    #from_f = file(from_ffield)
    #from_sections = parse_sections(from_f)
    #from_atom_dict = atom_section_to_dict(from_sections['atom'])
    #from_bond_dict = bond_section_to_dict(from_sections['bond'])
    #from_offdiag_dict = offdiag_section_to_dict(from_sections['offdiag'])
    #from_angle_dict = angle_section_to_dict(from_sections['angle'])
    #from_torsion_dict = torsion_section_to_dict(from_sections['torsion'])
    #from_hbond_dict = hbond_section_to_dict(from_sections['hbond'])
    
    from_f = Ffield()
    from_f.load(from_ffield)
    from_f.parse_sections()
    from_atom_dict = from_f.atom_section_to_dict()
    from_bond_dict = from_f.bond_section_to_dict()
    from_offdiag_dict = from_f.offdiag_section_to_dict()
    from_angle_dict = from_f.angle_section_to_dict()
    from_torsion_dict = from_f.torsion_section_to_dict()
    from_hbond_dict = from_f.hbond_section_to_dict()
    
    to_f = Ffield()
    to_f.load(to_ffield)
    to_f.parse_sections()
    to_atom_dict = to_f.atom_section_to_dict()
    to_bond_dict = to_f.bond_section_to_dict()
    to_offdiag_dict = to_f.offdiag_section_to_dict()
    to_angle_dict = to_f.angle_section_to_dict()
    to_torsion_dict = to_f.torsion_section_to_dict()
    to_hbond_dict = to_f.hbond_section_to_dict()
    
    #to_f = file(to_ffield)
    #to_sections = parse_sections(to_f)
    #to_atom_dict = atom_section_to_dict(to_sections['atom'])
    #to_bond_dict = bond_section_to_dict(to_sections['bond'])
    #to_offdiag_dict = offdiag_section_to_dict(to_sections['offdiag'])
    #to_angle_dict = angle_section_to_dict(to_sections['angle'])
    #to_torsion_dict = torsion_section_to_dict(to_sections['torsion'])
    #to_hbond_dict = hbond_section_to_dict(to_sections['hbond'])
    
    #Now create merged sections. Merge does the following:
    #1. Move over any entries that 'from' has, that 'to' doesn't have.
    #2. If additional move atoms are specified, those are also moved from 'from'
    #   to 'to' despite the conflict. The 'from' version will overwrite the 'to'
    #   version.
    merged_atom_dict = merge_atom_dict(from_atom_dict, to_atom_dict)
    #merged_atom_dict = merge_atom_dict(from_atom_dict, to_atom_dict, move_atoms)
    #print merged_atom_dict
   
    #Get the equivalent numbers of our move_atoms. We do this after we've merged
    #the atom_dicts.
    from_move_atoms_num = []
    to_move_atoms_num = []
    for atom_label in move_atoms:
        from_move_atoms_num.append(from_f.atom_num_lookup(atom_label))
        to_move_atoms_num.append(to_f.atom_num_lookup(atom_label))
    from_move_atoms_num = tuple(from_move_atoms_num)
    to_move_atoms_num = tuple(to_move_atoms_num)
    move_atoms_num = {'from': from_move_atoms_num, 'to': to_move_atoms_num}


    merged_bond_dict = merge_bond_dict(from_bond_dict, to_bond_dict)
    #merged_bond_dict = merge_bond_dict(from_bond_dict, to_bond_dict,
    #                                   move_atoms_num)
    #print merged_bond_dict

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

def merge_atom_dict(from_dict, to_dict, move_atoms = ()):
    '''
    Given two atom dicts (from and to) and also optional atoms to forcefully
    move over (the specified from atoms will overwrite the to atoms), will
    return a dictionary with merged atom entries.

    @param from_dict Dictionary where key is atom label and value are associated
                     atom lines. Entries from this dictionary will be moved over
                     to the 'to_dict'. If move_atoms are specified, then such
                     entries from this dictionary will replace the corresponding
                     entries in 'to_dict'.
    @param to_dict Dictionary where key is atom label and value are associated
                   atom lines. Entries from 'from_dict' will be merged into this
                   dictionary.
    @param move_atoms A list/set/tuple of atom_labels that will be moved from
                      'from_dict' to 'to_dict' regardless if the entry already
                      exists in 'to_dict'. (Optional)
    @return dict Merged dictionary from from_dict and to_dict.
    '''
    #NOTE: Instead of creating a separate merge_dict, we will just make all the
    #      changes on to_dict.
    for k, v in from_dict.iteritems():
        #If there is no conflict in merger, or if move_atoms say that we must
        #move the atom_label entry:
        if k not in to_dict or k in move_atoms:
            print 'Merged '+k
            to_dict[k] = v

    return to_dict

def merge_bond_dict(from_dict, to_dict, move_atoms_num = {'from': (), 'to': ()}):
    '''
    Given two bond dicts (from and to) and also optional atoms to forcefully
    move over (the specified from atoms will overwrite the to atoms), will
    return a dictionary with merged bond entries. For a bond entry to be
    forcefully copied over (possibly replacing any such existing entries in
    'to_dict'), both atoms involved in the bond must be specified in the
    move_atoms list.

    @param from_dict Dictionary where key is bond rep. and value are associated
                     bond lines. Entries from this dictionary will be moved over
                     to the 'to_dict'. If move_atoms are specified, then such
                     entries from this dictionary will replace the corresponding
                     entries in 'to_dict'.
    @param to_dict Dictionary where key is bond rep. and value are associated
                   bond lines. Entries from 'from_dict' will be merged into this
                   dictionary.
    @param move_atoms_num A dictionary of list/set/tuple of atom numbers that
                          will be moved from 'from_dict' to 'to_dict' regardless
                          if the entry already exists in 'to_dict'. Because atom
                          numbers in the 'from' file might be different than the
                          atom numbers in the 'to' file, move_atoms_num must be
                          a dictionary specifying the equivalent numbers for
                          both 'from' and 'to' files. (Optional) @return dict
                          Merged dictionary from from_dict and to_dict.
    '''
    #Make sure move_atoms_num in this case is a dictionary:
    try:
        move_atoms_num['from']
        move_atoms_num['to']
    except TypeError:
        print 'ERROR: move_atoms_num must be a dictionary of two tuples!' 
        sys.exit()

    #NOTE: Instead of creating a separate merge_dict, we will just make all the
    #      changes on to_dict.
    for k, v in from_dict.iteritems():
        #Deconstruct the key into atom numbers:
        from_atoms_in_bond = k.split('|')
        from_atoms_in_bond = map(int, from_atoms_in_bond) #Convert str to int
        from_atoms_in_bond = set(from_atoms_in_bond)
        #Now convert the atom numbers from 'from' to the equivalent atom numbers
        #in 'to'. For instance, if C is denoted 3 in 'from' but 4 in 'to', then
        #we make that conversion here (using list comprehension):
        if from_atoms_in_bond.issubset(move_atoms_num['from']):
            equiv_to_atoms_in_bond = [get_equivalent_atom_num(
                                            move_atoms_num['from'],
                                            move_atoms_num['to'],
                                            i) \
                                      for i in from_atoms_in_bond]
            equiv_to_atoms_in_bond = set(equiv_to_atoms_in_bond)
        else:
            #Not so elegant: We create a set with a negative number that we know
            #will NEVER be in the set move_atoms_num['to']. Therefore, the
            #.issubset() below will always evaluate to false.
            equiv_to_atoms_in_bond = set([-999])
        #If there is no conflict in merger, or if both atoms in our both are
        #specified in move_atoms:
        if k not in to_dict or \
            equiv_to_atoms_in_bond.issubset(move_atoms_num['to']):
            print 'Merged '+k
            to_dict[k] = v

    return to_dict

def get_equivalent_atom_num(from_atoms, to_atoms, from_atom_num):
    '''
    Given a list/tuple of from_atoms and to_atoms and also an atom number from
    the from_atom list, returns the equivalent atom number from the to_atoms
    list.

    @param from_atoms List/tuple of atom numbers.
    @param to_atoms List/tuple of atom numbers that has equivalent ordering as
                    the from_atoms list.
    @param from_atom_num An atom number from the from_atoms list that we are
                         trying to convert to a 'to' atom number.
    @return int Equivalent atom num that is in the 'to_atoms' list.
    '''
    from_atoms = list(from_atoms) #Must be list to use .index() method
    
    try:
        i = from_atoms.index(from_atom_num)
    except ValueError:
        print 'ERROR: Atom number '+str(from_atom_num)+" does not "+\
              "exist in 'from' list"
        sys.exit()

    try:
        to_atoms[i]
    except IndexError:
        print 'ERROR: Index '+str(i)+" does not "+\
              "exist in 'to' list"
        sys.exit()


    return to_atoms[i]




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
