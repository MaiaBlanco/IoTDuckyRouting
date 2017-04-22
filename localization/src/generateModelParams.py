#! /usr/bin/python
# File to read json data collected for multiple points in 
#the room around the access points, calculate the distances
#to each AP, and generate model parameters for each AP

from __future__ import print_function
import iwlist
import pprint
import re
import sys
import json
import numpy as np
# So we can use spaceDist.euclidean(p1, p2):
import scipy.spatial.distance as spaceDist


# Reference distance in meters:
REF_DIST = 1
# Access point SSIDs:
ESSIDs = ["IOT-AP01", "IOT-AP02", "IOT-AP03", "IOT-AP04"]
# World coordinates in cm for each Access point:
'''Access Point	|	x, y, z	from origin (cm) 	|
IOT-APO1		|	122, 1.5, 201.5				|
IOT-APO2		|	177.5, 531.5, 204			|
IOT-APO3		|	672.5, 531.5, 202.5			|
IOT-AP04		|	640, 1.5, 201				|'''
COORDS = \
{
	"IOT-AP01":[122, 1.5, 201.5],
	"IOT-AP02":[177.5, 531.5, 204],
	"IOT-AP03":[672.5, 531.5, 202.5],
	"IOT-AP04":[640, 1.5, 201]	
}
# CSV output files for each AP to generate best-fit line in excel or some other tool:
AP_CSV_FILES = {}
# reference to pretty print function:
pp = pprint.PrettyPrinter(indent=4)


# Algorithms for finding distance:
# Simple RSSI signal model -- prone to noise -- these perform map RSSI to distance
#	lognormal shadowing path loss model
#	Nakagami fading model
#	Rayleigh Fading Model
#	Ricean fading model
# Weighted least squares, as in Tarrio et al. paper:
#	Hyperbolic
#	Circular


# Models to generate params:
# 1. Lognormal shadowing:
	# A is const term - determined experimentally and supplied for each AP
	# eta is path loss exponent - Experimentally determined, eta in [2..4]
	# N is zero mean gaussian variable with std dev = sig
	# Solve for 
	# recvPower = A - 10*eta*log(d/d_0) + N
	# Assuming d_0 = 1 meter for all models
# 2. 







if __name__ == "__main__":
	# Check user input
	if len(sys.argv) != 2:
		eprint("USAGE: {} output_filename.json".format(sys.argv[0]))
		sys.exit(1)
	file = sys.argv[1]
	with open(file, 'r') as f:
		data = f.read()
		dataPoints = json.loads(data);
		for AP in ESSIDs:
			AP_CSV_FILES[AP] = open("../data/"+AP+".csv", 'w')

# For each point in the dataset, calculate the distance from each AP and print as separate CSVs the following:
# distance to AP, dbm value
	for point, value in dataPoints.items():
		point_coord = [float(x) for x in point.strip('(').strip(')').split(", ")]
		print("Point coord: {}".format(point_coord))
		# Each value corresponding to point_coord has 20 samples for each access point
		for AP in ESSIDs:
			dist = spaceDist.euclidean(COORDS[AP], point_coord)
			for sample in value[AP]:
				AP_CSV_FILES[AP].write("{}, {}\n".format(dist, sample["dbm_level"]))
				

