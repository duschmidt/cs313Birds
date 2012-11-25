import numpy as np
from random import randint
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Colormap


def sumOfNeighbors(a):
	new = np.zeros(a.shape)
	new = np.roll(a,1,0)+np.roll(a,1,1)+np.roll(a,-1,0)+np.roll(a,-1,1)
	return new
f = open('dump.pkl','rb')
import cPickle as cp
m = cp.load(f)
f.close()

a1 = m['Bird']['diffused']
a2 = m['Hawk']['diffused']

s = a1 - a2
import math
mn = math.fabs(np.min(s))

s += np.ones(s.shape)*mn

s *= m['Obs']


plt.subplot(221)
imgplt = plt.imshow(a1,interpolation='none', norm=LogNorm())
plt.colorbar()

plt.subplot(222)
imgplt = plt.imshow(a2,interpolation='none', norm=LogNorm())
plt.colorbar()

plt.subplot(223)
imgplt = plt.imshow(s, interpolation='none', norm=LogNorm())
plt.colorbar()


plt.show()