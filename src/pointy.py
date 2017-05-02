#!/usr/bin/env python

from collections import namedtuple
from math import sqrt
from math import log

point=namedtuple("point","x y z")

def pdist2(p1,p2):
	return (p1.x-p2.x)**2+(p1.y-p2.y)**2+(p1.z-p2.z)**2

def pdist(p1,p2):
	return sqrt(pdist2(p1,p2))
