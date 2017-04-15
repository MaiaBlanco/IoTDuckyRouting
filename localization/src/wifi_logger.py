#! /usr/bin/python
# Script to get signal strength data for multiple access points and log each value based on the current location.
from __future__ import print_function
import iwlist
import pprint
import re
import sys
import json

# Add the names of any access points/ESSIDs to scan here
ESSIDs = ["IOT-AP01", "IOT-AP02", "IOT-AP03", "IOT-AP04"]
NUM_SAMPLES = 5
# Store associated MAC addresses when found to this dict
AP_Dict = {}
# log data indexed by x,y location
points = {}
pp = pprint.PrettyPrinter(indent=4)


# Error printing
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def logPoints(SSID_List):
	dataPoints = {}
	# Create regex for coordinates (positive floating point numbers)
	coordRe = re.compile(r"\s*(?P<x>\d+.?\d*)\s+(?P<y>\d+.?\d*)\s+(?P<z>\d+.?\d*)$")
	print("To exit and save the data, type 'exit' at any time.")
	while True:
		reSuccess = False;
		coordString = raw_input("Enter the x, y, and z coordinate to log, in CM.\nEnter them in cm, as floats, separated by spaces:")
		if coordString.lower() == "exit":
			return dataPoints
		searchResult = coordRe.search(coordString)
		if searchResult:
			searchDict = searchResult.groupdict()
			if "x" in searchDict and "y" in searchDict and "z" in searchDict:
				reSuccess = True
				print("Success! Getting {} datapoints now.".format(NUM_SAMPLES))
				point = "({}, {}, {})".format(float(searchDict['x']), float(searchDict['y']), float(searchDict['z']))
				if point in dataPoints:
					print("Warning: point {} already exists. Overwrite? (y/n)".format(point))
					yN = str(raw_input())
					if yN.lower().strip() == 'n':
						continue
				dataPoints[point] = { x:list() for x in SSID_List }
				for i in range(NUM_SAMPLES):
					values = SSIDScan(SSID_List)
					for SSID in SSID_List:
						dataPoints[point][SSID].append(values[SSID])
			else:
				eprint("ERROR: Some values (x y z) missing from coordinate...")
		else:
			eprint("ERROR: Invalid x y z coordinate. Try again...")
			continue
	return dataPoints

def SSIDScan(SSID_List):
	rawData = iwlist.scan() # No arg since defaults to wlan0
	cells = iwlist.parse(initScan)
	ssids = [x for x in cells if x["essid"] in SSID_List]
	tags = ["quality", "quality_total", "dbm_level", "signal_level", "signal_total"]
	data = { x["essid"] : {k:v for k,v in x.iteritems() if k in tags} for x in ssids}
	return data

# Upon entry of a new x, y position, verify the data entry
# Then take 20 measurements using iwlist scanner and parse the data
# Store the information in memory:
	# For each coordinate to be scanned:
		# Store in dictionary a dictionary:


if __name__ == "__main__":
	if len(sys.argv) != 2:
		eprint("USAGE: {} output_filename.json".format(sys.argv[0]))
		sys.exit(1)
	fname = sys.argv[1]
	# Get initial scan to verify that APs are present and record MACs:
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
	# Log some data:
	results = logPoints(ESSIDs)
	f = open(fname, 'w')
	f.write(json.dumps(results, ensure_ascii=False, indent=4, sort_keys=True))
	f.close()



#cells = iwlist.parse(rawData) # Get the cells for this point