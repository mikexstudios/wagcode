#!/usr/bin/env python

import os
import re

sq_cmd = os.popen('showq|grep $USER')
for line in sq_cmd:
	sq_jobid_regex = re.match(r'(\d+)\s+.*', line)
	#Need to check sq_jobid_regex first in case we didn't match.
	if sq_jobid_regex:
		print 'Killing: '+sq_jobid_regex.group(1)
		os.system('qdel '+sq_jobid_regex.group(1))
