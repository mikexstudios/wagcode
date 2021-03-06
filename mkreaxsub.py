#!/usr/bin/python
'''
mkreaxsub.py
-----------------
Creates a ReaxFF PBS submission file that uses node scratch /temp1
directory. Cool features include:
1. The submission file is written below as a template so it is
   extremely easy to view and modify.
2. cptonode [file] -> command to copy a file to the node's
                      simulation directory (ie. control).
   cpfromnode [file] -> command to copy a file from the node's
                        simulation directory (ie. fort.71).
						Note: If [file] is * (all files) you have
						to input * as \* so that the shell doesn't
						misinterpret it.
   nodesh [command] -> execute a command on the node (the working
                       directory is the node's simulation dir.
3. Before the simulation output files are copied back, the amount
   of free space the user has is checked against the total file
   size of the simulation output files. If the user does not have
   enough space to accomodate the files, then they aren't copied
   back.

USAGE: mkreaxsub [pbs_name]

$Id:$
'''
__author__ = 'Michael Huynh (mikeh@caltech.edu)'
__website__ = 'http://www.mikexstudios.com'
__copyright__ = 'General Public License (GPL)'

import os, sys #Used for path finding
import random

#Parameters (you can change these if you like)
pbs_sub_file = 'reax.run'
current_dir = os.getcwd()
this_script_dir = os.path.abspath(os.path.dirname(sys.argv[0])) #no trailing slash
#this_script_name = os.path.basename(sys.argv[0]) #in case this script is renamed

#PBS submission file template. Do NOT delete bracketed items since we will
#replace them with the correct values (ie. [pbsname] -> the name for the run).
# PBS -m ea sends mail to us when job is complete
# PBS -q workq seems to be something for WAG servers
pbs_template = '''
#PBS -l nodes=1:ppn=1,walltime=200:00:00
#PBS -q workq
#PBS -N [pbsname]
#PBS -m ea
#PBS -e [currentpath]/pbs.err
#PBS -o [currentpath]/pbs.out
#!/bin/bash

#Output some information related to this job:
#sed is used to remove the extra information from the names.
#We don't have access to $REMOTEHOST so we need to use the $PBS_O_HOST
cluster_name=`echo $PBS_O_HOST | sed 's/\..*//g'`
node_name=`echo $HOSTNAME | sed 's/\..*//g'`
curr_dir=[currentpath]

cd ${curr_dir}
echo "Cluster: ${cluster_name}" > info.pbs
echo "Hostname: ${node_name}" > info.pbs
echo "Job ID: ${PBS_JOBID}" >> info.pbs
echo "Temp Directory: [pbstempdir]" >> info.pbs  

#Define temp directory
temp_dir=/temp1/${USER}/[pbstempdir]

#Generate some small scripts for copying files to and from the node.
#And also removing the simulation from the node...
env | grep hive
echo "rsh ${cluster_name} \\"rsh ${node_name} cd ${temp_dir}\;"'$1"' > nodesh
echo "CMD=\\"rsh ${cluster_name} rsh ${node_name} \\\\\\"cp -r ${curr_dir}/"'$1'" ${temp_dir}/\\\\\\"\\"" > cptonode
echo "echo \$CMD; \$CMD" >> cptonode
echo "CMD=\\"rsh ${cluster_name} rsh ${node_name} \\\\\\"cp -r ${temp_dir}/"'$1'" ${curr_dir}/\\\\\\"\\"" > cpfromnode
echo "echo \$CMD; \$CMD" >> cpfromnode
echo "CMD=\\"rsh ${cluster_name} rsh ${node_name} \\\\\\"rm -rf ${temp_dir}/\\\\\\"\\"" > removefromnode
echo "echo \$CMD; \$CMD" >> cpfromnode
chmod 755 nodesh
chmod 755 cptonode
chmod 755 cpfromnode
chmod 755 removefromnode

#Copy files to the node. To combat issues with the same pbsname, we
#append a short hash to the directory name (generated in the python script).
mkdir ${temp_dir}
cd ${temp_dir}
cp ${curr_dir}/* .

#Run ReaxFF
exe

#Check disk quota. Copy files back only if we have enough disk space.
output_size=`du -s . | awk '{print $1}'`
#We have do remove the /net/hulk/home# line now since hulk's nodes report chq
#differently!
space_left=`chq | grep '/net/hulk' | sed -r 's/[a-z\/]+[0-9]+[ ]*//g' | awk '{print $2-$1}'`
echo "Total size of files: ${output_size}."
if [ "${output_size}" -lt "${space_left}" ]; then
	echo 'Copying files back...'
	cp * ${curr_dir}/
else
	echo "Not enough disk space to copy files back! You'll have to manually copy these..."
fi
'''

#Now search and replace template tags with our values:
pbs_name = sys.argv[1]
pbs_template = pbs_template.replace('[pbsname]', pbs_name)
pbs_template = pbs_template.replace('[currentpath]', current_dir)
pbs_template = pbs_template.replace('[scriptdir]', this_script_dir)
#For the pbstempdir, we want to generate a short random string to tag on the end
#Technically, we can add a check here to see if the temp directory exists. If
#not, then we can just skip this random generation step. However, I think this
#is good, in general, since there are cases where people might reuse the same
#PBS script or if they run this later and have a conflicting directory.
pbs_temp_dir = pbs_name+'_'+str(random.randint(1000,9999)) #4 digits should be good enough...
pbs_template = pbs_template.replace('[pbstempdir]', pbs_temp_dir)

#Write to sub file:
f = open(pbs_sub_file, 'w')
#print pbs_template
f.write(pbs_template)
f.close()

print pbs_sub_file+' created!'
