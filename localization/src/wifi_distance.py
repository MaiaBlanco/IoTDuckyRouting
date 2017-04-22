#! /usr/bin/python
# Script to get signal strength data for multiple access points and log each value based on the current location.
from __future__ import print_function
import iwlist
import pprint
import re
import sys
import json
import numpy as np

# Add the names of any access points/ESSIDs to scan here:
ESSIDs = ["IOT-AP01", "IOT-AP02", "IOT-AP03", "IOT-AP04"]
# number of samples to keep for techniques like moving average:
NUM_SAMPLES = 10
# reference to pretty print function:
pp = pprint.PrettyPrinter(indent=4)


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
			print("Used dbm level for {}".format(SSID))
		else if "signal_level" in values[SSID].keys() and \
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

if __name__ == "__main__":
	# Check user input
	if len(sys.argv) != 2:
		eprint("USAGE: {} output_filename.json".format(sys.argv[0]))
		sys.exit(1)
	# Open log file
	fname = sys.argv[1]
	# Get initial scan to verify that APs are present:
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
	# start getting data:
	samples = { x:np.array() for x in ESSIDs }
	averages = { x:0.0 for x in ESSIDs }
	print("Getting {} samples to start localizing...".format(NUM_SAMPLES))
	for i in range(NUM_SAMPLES):
		results = getAPSignals(ESSIDs)
		for SSID in ESSIDs:
			samples[SSID].append(results[SSID])
	# Now continue recording new data and moving the window average along the array:
	while True:
		results = getAPSignals(ESSIDs)
		for SSID in samples.keys():
			averages[SSID] = mean(samples[SSID])
			samples[SSID] = np.roll(samples[SSID], -1)
			samples[SSID][-1] = results[SSID]
	# f = open(fname, 'w')
	# f.write(json.dumps(results, ensure_ascii=False, indent=4, sort_keys=True))
	# f.close()



# Algorithms for finding distance:
# Simple RSSI signal model -- prone to noise -- these perform map RSSI to distance
#	lognormal shadowing path loss model
#	Nakagami fading model
#	Rayleigh Fading Model
#	Ricean fading model
# Weighted least squares, as in Tarrio et al. paper:
#	Hyperbolic
#	Circular


def lognormalShadowingModel():
	# A is const term - determined experimentally and supplied for each AP
	# eta is path loss exponent - Experimentally determined, eta in [2..4]
	# N is zero mean gaussian variable with std dev = sig
	# Solve for 
	# recvPower = A - 10*eta*log()