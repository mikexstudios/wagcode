#!/usr/bin/env python
'''
Struct.py
-----------------
A simple class to represent a structure.
The solution comes from:
http://www.velocityreviews.com/forums/t373406-does-python-provide-quotstructquot-data-structure.html
'''
__version__ = '0.1.0'
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

class Struct():
	def __init__(self, *args, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
