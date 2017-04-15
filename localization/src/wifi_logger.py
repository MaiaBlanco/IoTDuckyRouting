#! /usr/bin/python
# Script to get signal strength data for multiple access points and log each value based on the current location.
import iwlist
import pprint
import re
import sys

# Add the names of any access points/ESSIDs to scan here
ESSIDs = ["AP01", "AP02", "AP03", "AP04"]
NUM_SAMPLES = 20
# Store associated MAC addresses when found to this dict
AP_Dict = {}
# log data indexed by x,y location
points = {}



if __name__ == "__main__":
	# Get initial scan to verify that APs are present and record MACs:
	initScan = iwlist.parse()
	cells = [x for x in iwlist.parse(rawData) if x["essid"] in ESSIDs]
	if len(cells) < len(ESSIDs):
		eprint("ERROR: Can't find all of the ESSIDs specified!")
		eprint("Found:")
		eprint([ x["essid"] for x in cells ])
		eprint("Need:")
		eprint( ESSIDs )
		sys.exit(1)
	sys.exit(0)
	coordRe = re.compile(r"\s*(?P<x>-?\d+.?\d*)\s+(?P<y>-?\d+.?\d*)$")
	coordString = raw_input("Enter the x, y, and z coordinate to log, in CM.\nEnter them in cm, as floats, separated by spaces:")
	searchResult = coordRe.search(coordString)
	if searchResult:
		searchDict = searchResult.groupdict()
		if "x" in searchDict and "y" in searchDict and "z" in searchDict:
			for i in range(20):
				rawData = iwlist.scan() # No arg since defaults to wlan0

# Upon entry of a new x, y position, verify the data entry
# Then take 20 measurements using iwlist scanner and parse the data
# Store the information in memory:
	# For each coordinate to be scanned:
		# Store in dictionary a dictionary:



#cells = iwlist.parse(rawData) # Get the cells for this point




def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)