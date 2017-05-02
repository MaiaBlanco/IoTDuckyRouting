#! /usr/bin/python
# Script to get signal strength data for multiple access points and log each value based on the current location.
from __future__ import print_function
import iwlist
import pprint
import re
import sys
import json
import numpy as np
import math
from circular_estimator import weightedCircularEstimator
from circular_estimator import stdCircularEstimator
from scipy import stats
from scipy.optimize import brentq

# Weighted or standard circular estimator:
method = 'weighted'
# Add the names of any access points/ESSIDs to scan here:
ESSIDs = ["IOT-AP01", "IOT-AP02", "IOT-AP03", "IOT-AP04"]
# number of samples to keep for techniques like moving average:
NUM_SAMPLES = 10
# reference to pretty print function:
pp = pprint.PrettyPrinter(indent=4)
# Lognormal distance model parameters (A, eta, R^2):
LN_AP_PARAMS = \
{
	"IOT-AP01":(-35.481, -1.8134, 0.4124 ),
	"IOT-AP02":(-34.308, -1.9197, 0.6073 ),
	"IOT-AP03":(-33.712, -2.0273, 0.5873 ),
	"IOT-AP04":(-32.598, -1.4818, 0.4727 )
}
# Second order log fit parameters (ax^2 + bx + c), for x = log(d/1meter)
SECORD_AP_PARAMS = \
{
	"IOT-AP01":( 3.51, -20.08, -35.77 ),
	"IOT-AP02":( 4.367, -19.307,  -35.387 ),
	"IOT-AP03":( 4.189, -20.587, -35.351 ),
	"IOT-AP04":( 0.3664, -14.808, -32.76 )
}
AP_COORDS = \
[
        [122, 1.5, 201.5],
	[177.5, 531.5, 204],
	[672.5, 531.5, 202.5],
	[640, 1.5, 201]	
]

# Error printing
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def getAPSignals(SSID_List):
	dataPoints = {}
	print("Getting datapoints for {} APs now.".format(len(SSID_List)))
	values = SSIDScan(SSID_List)
	for SSID in SSID_List:
		if "dbm_level" in values[SSID].keys():
			dataPoints[SSID] = float(values[SSID]["dbm_level"])
			#print("Used dbm level for {}".format(SSID))
		elif "signal_level" in values[SSID].keys() and \
		"signal_total" in values[SSID].keys():
			dataPoints[SSID] = float(values[SSID]["signal_level"])/\
			float(values[SSID]["signal_total"])
			print("Used signal level for {}".format(SSID))
		else:
			eprint("Could not find any useful data for AP {}".format(SSID))
			dataPoints.append(0.0)
			continue
	return dataPoints

def SSIDScan(SSID_List):
	rawData = iwlist.scan() # No arg since defaults to wlan0
	cells = iwlist.parse(rawData)
	ssids = [x for x in cells if x["essid"] in SSID_List]
	tags = ["quality", "quality_total", "dbm_level", "signal_level", "signal_total"]
	data = { x["essid"] : {k:v for k,v in x.iteritems() if k in tags} for x in ssids}
	return data

# Algorithms for finding distance:
# Simple RSSI signal model -- prone to noise -- these perform map RSSI to distance
#	lognormal shadowing path loss model
# 	2nd order lognormal fit model
# Weighted least squares, as in Tarrio et al. paper:
#	Circular - standard and weighted

# Return distance to AP in cm based on measured RSS and A, eta parameters for AP
def lognormalShadowingModel(RSS, A, eta):
	# A is const term - determined experimentally and supplied for each AP
	# eta is path loss exponent - Experimentally determined, eta in [2..4]
	# N is zero mean gaussian variable with std dev = sig
	# Solve for 
	# recvPower = A - 10*eta*log(d/d_0) + N
	# Assuming d_0 = 1 meter (100cm) for all models
	# Can't model N, so just have A and eta as input params
	return math.pow( 10, (RSS - A) / (10*eta) ) * 100

# Return distance to AP in cm based on measured RSS and c1, c2, c3 params for AP:
def secondOrderShadowingModel(RSS, c1, c2, c3):
	def quadratic(x,a,b,c):
    	return a*x**2 + b*x - c - RSS
    res = brentq(quadratic, -2.0, 2, args=(c1, c2, c3-RSS))
	return math.pow( 10, res) * 100

distances = [0,0,0,0]
# For RSS values get an XYZ estimate based on the circular estimator model
def localize(ESSIDs, LN_AP_PARAMS, num_samples=20, samples={}, z_height=-1, coordinates=[0,0,0], circType='weighted', stat='mean'):
	# If we don't already have enough samples, get them:
	if not bool(samples) or sorted(ESSIDs) != sorted(samples.keys() or len(samples[ESSIDs[0]]) < num_samples):
		print("Getting {} new samples.".format(num_samples))
		samples = { ssid:np.zeros(num_samples) for ssid in ESSIDs}
		for i in range(num_samples):
			results = getAPSignals(ESSIDs)
			for SSID in ESSIDs:
				samples[SSID][i] = results[SSID]
	# Now continue recording new data and moving the window along the array:
	results = getAPSignals(ESSIDs)
	SSID_keys = sorted(samples.keys())
	for i in range(len(SSID_keys)):
		SSID = SSID_keys[i]
		# circulate the moving average window:
		samples[SSID] = np.roll(samples[SSID], -1)
		samples[SSID][num_samples-1] = results[SSID]
		# Apply the selected statistic:
		if stat == 'mean':
			stat_value = np.mean(samples[SSID])
		elif stat == 'median':
			stat_value = np.median(samples[SSID])
		elif stat == 'mode':
			[hist, bin_edges] = np.histogram(samples[SSID], 20)
			idx = np.argmax(hist)
			stat_value = bin_edges[idx]
		else:
			eprint("ERROR: invalid statistic. Choose from ['mean', 'median', 'mode']")
			return None
		# Find the distance using the lognormal model:
		distances[i] = lognormalShadowingModel( stat_value, \
			LN_AP_PARAMS[SSID][0], LN_AP_PARAMS[SSID][1] )
		# Used the second order lognormal model:
		distances[i] = secondOrderShadowingModel( stat_value, \
			SECORD_AP_PARAMS[SSID][0], SECORD_AP_PARAMS[SSID][1], SECORD_AP_PARAMS[SSID][2] )
		print("Distance from AP {}: {} cm".format(SSID, distances[i]))

	# Now get an estimate of where we are:
	if circType == 'weighted':
		if z_height == -1:
			min_result = weightedCircularEstimator(distances, AP_COORDS, coordinates)
		else:
			min_result = weightedCircularEstimator(distances, AP_COORDS, coordinates, z=z_height)
	elif circType == 'std':
		if z_height == -1:
			min_result = stdCircularEstimator(distances, AP_COORDS, coordinates)
		else:
			min_result = stdCircularEstimator(distances, AP_COORDS, coordinates, z=z_height)
	else:
		eprint("ERROR: invalid circular estimator type! (Needs 'weighted' or 'std')")		
                return None
	return (samples, min_result)

if __name__ == "__main__":
	# Check user input
	if len(sys.argv) < 2:
		eprint("USAGE: {} <-1 or given z height.> <OPTIONAL: 'weighted' or 'standard' for different circular estimators".format(sys.argv[0]))
		sys.exit(1)
	z_height = float(sys.argv[1])
	if len(sys.argv) == 3:
		if str(sys.argv[2]) == 'std':
			circType = 'std'
		elif str(sys.argv[2]) == 'weighted':
			circType = 'weighted'
		else:
			# default is weighted
			circType = 'weighted'
	#Get initial scan to verify that APs are present:
	initScan = iwlist.scan()
	cells = iwlist.parse(initScan)
	cells = [x for x in cells if x["essid"] in ESSIDs]
	if len(cells) < len(ESSIDs):
		eprint("ERROR: Can't find all of the ESSIDs specified!")
		eprint("Found:")
		eprint([ x["essid"] for x in cells ])
		eprint("Need:")
		eprint( ESSIDs )
		sys.exit(1)
	print("Successfully found {} SSIDs:".format(len(ESSIDs)) )
	[ print(x["essid"], end=" ") for x in cells ]
	print()

	samples = { x:np.zeros(NUM_SAMPLES) for x in ESSIDs }
	distances = [ 0.0 for x in ESSIDs ]
	print("Getting {} samples to start localizing...".format(NUM_SAMPLES))
	for i in range(NUM_SAMPLES):
		results = getAPSignals(ESSIDs)
		for SSID in ESSIDs:
			samples[SSID][i] = results[SSID]
	coordinates = [0,0,0]
	while True:
		(samples, min_result) = localize(ESSIDs, LN_AP_PARAMS, num_samples=NUM_SAMPLES, \
			samples=samples, z_height=z_height, coordinates=coordinates, circType='weighted',\
			 stat='median')
		if min_result is not None:
			coordinates = min_result[:]
			print("Estimated Coordinates:\tx: {:10.4f}\ty: {:10.4f}\tz: {:10.4f}".format(coordinates[0], coordinates[1], coordinates[2]))
		else:
			eprint("ERROR: result of minimization was NONE! Skipping...")
