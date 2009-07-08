#!/bin/awk -f
# AWK script to calculate average pressure
# by Michael Huynh (mikeh@caltech.edu)
# Usage: awk -f calc_avg_pressure.awk fort.71

{ if(NR > 1) {
	entries++;
	pres_sum += $12; 
	} 
}
END { print "Total pressure: " pres_sum " Total number of entries: " entries; 
	  print "Average pressure: " pres_sum/entries;
	}
