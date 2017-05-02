#!/usr/bin/env python

from collections import namedtuple
from scipy.optimize import minimize
from math import sqrt
from math import log

point=namedtuple("point","x y z")

zpos=90

APL=(0,	point(122,1.5,201.5),
		point(177.5,531.5,204),
		point(672.5,531.5,202.4),
		point(640,1.5,201))


def pdist2(p1,p2):
	return (p1.x-p2.x)**2+(p1.y-p2.y)**2+(p1.z-p2.z)**2

def pdist(p1,p2):
	return sqrt(pdist2(p1,p2))

err=[0,0,0,0,0]
def heuristicfit(loc):
	#p=point(loc[0],loc[1],loc[2])
	p=point(loc[0],loc[1],zpos)
	errsum=0;
	for i in range(1,5):
		err[i]=(pdist(APL[i],p)-realD[i])**2
		errsum=errsum+err[i]*wgt[i]
	return errsum

answer=point(422,383,zpos)
realD=[0,pdist(answer,APL[1])
		,pdist(answer,APL[2])
		,pdist(answer,APL[3])
		,pdist(answer,APL[4])]

realD=[0,901,202,137,511];
nwgt=[0,1,1,1,1]
wgt=[0,1,1,1,1]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if (res.success):
	print('\nAll APs')
	print(res.x)
	prx=point(res.x[0],res.x[1],zpos)
	print(pdist(prx,answer))

wgt=[0,0,1,1,1]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if res.success:
	nwgt[1]=(res.fun)*0.4124
	print(res.x)
else:
	print('ERROR in AP01')

wgt=[0,1,0,1,1]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if res.success:
	nwgt[2]=(res.fun)*0.6073
	print(res.x)
else:
	print('ERROR in AP01')

wgt=[0,1,1,0,1]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if res.success:
	nwgt[3]=(res.fun)*0.5873
	print(res.x)
else:
	print('ERROR in AP01')

wgt=[0,1,1,1,0]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if res.success:
	nwgt[4]=(res.fun)*0.4727
	print(res.x)
else:
	print('ERROR in AP01')

print(nwgt)

wgt=nwgt
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if (res.success):
	print('\nAll APs (normalized)')
	print(res.x)
	prx=point(res.x[0],res.x[1],zpos)
	print(pdist(prx,answer))
else:
	print('ERROR IN normal')

for i in range(1,5):
	wgt[i]=sqrt(nwgt[i])
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if (res.success):
	print('\nAll APs (root-normalized)')
	print(res.x)
	prx=point(res.x[0],res.x[1],zpos)
	print(pdist(prx,answer))
else:
	print('ERROR IN root-normal')

for i in range(1,5):
	wgt[i]=log(nwgt[i])
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if (res.success):
	print('\nAll APs (log-normalized)')
	print(res.x)
	prx=point(res.x[0],res.x[1],zpos)
	print(pdist(prx,answer))
else:
	print('ERROR in log-normal')

for i in range(1,5):
	wgt[i]=1/nwgt[i]
res=minimize(heuristicfit, [0,0,0], method='SLSQP')
if (res.success):
	print('\nAll APs (log-normalized)')
	print(res.x)
	prx=point(res.x[0],res.x[1],zpos)
	print(pdist(prx,answer))
else:
	print('ERROR in log-normal')
