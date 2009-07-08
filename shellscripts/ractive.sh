#!/bin/bash

#if [ "$1" == "" ];  then
#    server="hive"
#else
#    server=$1
#fi

rsh hive "showq|grep Active"
rsh matrix "showq|grep Active"
rsh borg "showq|grep Active"
