#! /usr/bin/env python

import copy

rows = 24
cols = 10

a = [0 for x in range(0,cols)]

for y in (range(0, rows)):
	for x in range(0, cols):
		print(y,x)
		if 1:
			a[x] += 1 << y%12
			#print(a)

	#print(y%12)
	if y%12 == 0 and y>0:
		
		#headNumber, headVals = enumerate(a)
		#print(headNumber,headVals)

		#for column, firingVal in enumerate(a):
			#if firingVal:
				#print(column,firingVal)

		#print(a)
		a = [0 for x in range(0,cols)]
		a = [copy.copy(a) for x in range(0,2)]