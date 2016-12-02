import numpy as np
import scipy as sp
import time

def f1(x):
	return 2+ 12*x + 20*x**2 + 18*x**3;

def secretShare(k, n, myPolValue, sharedValues, colabValues, partnerNbr, colabPartners):
	CalcF1 = myPolValue + sum(sharedValues);
	y = [CalcF1];
	for i in range (0, len(colabValues)):
		y.append(colabValues[i]); # adds all y values. 
	x = [partnerNbr]; # Inserts the partner number. (participant 1 out of 8 for example)
	for i in range (0, len(colabPartners)):
		x.append(colabPartners[i]);
	coeff = np.polyfit(x, y, k-1); # creates the coeff for k-1 degree poly.
	return np.polyval(coeff, 0);

print(secretShare(4, 6, f1(1), [44, 23, 34, 41, 42], [2930, 11816, 19751], 1, [3,5,6]));


