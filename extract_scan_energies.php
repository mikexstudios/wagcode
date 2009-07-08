#!/usr/bin/php -q
<?php
/**
 * Extract out scan angles and widths from Jaguar out file.
 * by Michael Huynh (http://www.mikexstudios.com)
 */

$f = file($argv[1]);
$out = fopen('scan.tsv', 'w');

foreach($f as $num=>$line)
{
	if(preg_match('/Geometry scan step\s+(\d+)\s+.+/', $line, $matches))
	{
		#echo $matches[1]+' ';	
		if(preg_match('/scan:\s+s = (\d+\.?\d*)\s+energy =\s+(-?\d+\.?\d*)\s*/', $f[$num+1], $sub_matches))
		{
			#echo $sub_matches[1].' '.$sub_matches[2]."\n";

			//Write tab separate values to file
			fwrite($out, $matches[1]."\t".$sub_matches[1]."\t".$sub_matches[2]."\n");
			echo $matches[1]."\t".$sub_matches[1]."\t".$sub_matches[2]."\n";
		}
		//echo $f[$num+1]."\n";
	}
}

fclose($out);
?>
