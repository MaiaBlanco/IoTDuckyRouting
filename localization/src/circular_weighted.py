#! /usr/bin/python

from __future__ import print_function
from scipy.optimize import minimize
import numpy as np
import math
import pointy
from scipy.spatial.distance import euclidean

# Error printing
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


# Given a list of distances to each access point, the locations of each AP,
# a starting guess x0=(x,y,z), and an optionally specified z coordinate:
# Return the best estimation of x,y,z and the residual of the estimation.
def weightedCircularEstimator(dists, AP_list, x0, z=-1):
	d = np.array(dists)	
	# Define the two options for optimization functions using 
	#the weighted circular estimator:
	# Optimize over x,y GIVEN z
	def weightedCircularFun2(in_loc, z_val, distances, APs):
		in_loc = in_loc.append(z_val)
		acc = 0.0;
		for i in range(len(distances)):
			acc += (euclidean( APs[i], np.array(in_loc) ) - distances[i])/(distances[i]**2)
	# Optimize over x,y,and z
	def weightedCircularFun3(in_loc, distances, APs):
		acc = 0.0;
		for i in range(len(distances)):
			acc += (euclidean( APs[i], np.array(in_loc) ) - distances[i])/(distances[i]**2)
	
	room_dimensions = [(0,812), (0, 533), (0, 400)] # In cm, as with everything else here
	if z != -1:
		loc = loc[:2]
		res = minimize(weightedCircularFun2, x0, args=(z, dists, AP_list), bounds=room_dimensions[:2])
	else:
		res = minimize(weightedCircularFun3, x0,  args=(dists, AP_list), bounds=room_dimensions)
	if not res[2]:
		eprint("ERROR: Could not find x,y,z given the input distances. :(")
		eprint("Message: "+res[3])
		return None
	else:
		if len(res[1]) == 2:
			return res[1].append(z)
		else:
			return res[1]