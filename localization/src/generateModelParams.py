# File to read json data collected for multiple points in 
#the room around the access points, calculate the distances
#to each AP, and generate model parameters for each AP

# Models to generate params:
# 1. Lognormal shadowing





if __name__ == "__main__":
	# Check user input
	if len(sys.argv) != 2:
		eprint("USAGE: {} output_filename.json".format(sys.argv[0]))
		sys.exit(1)
	file = 