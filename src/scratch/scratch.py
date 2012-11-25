import numpy as np
from random import randint
import matplotlib.pyplot as plt

dim = 100

a = np.zeros((dim, dim),dtype=np.float)
b = np.zeros((dim, dim),dtype=np.float)
obs = np.ones(a.shape)

obs[:,0]=0
obs[:,dim-1]=0
obs[0,:]=0
obs[dim-1,:]=0

# left = True
# for i in range(0,dim,25):
# 	if left:
# 		obs[i,10:]=0
# 	else:
# 		obs[i,:-10]=0
# 	left = not left

def sumOfNeighbors(a):
	new = np.zeros(a.shape)
	new = np.roll(a,1,0)+np.roll(a,1,1)+np.roll(a,-1,0)+np.roll(a,-1,1)
	return new

# for i in range(int(dim**2*0.001)):
# 	a[randint(0,dim-1),randint(0,dim-1)]=100
# 	b[randint(0,dim-1),randint(0,dim-1)]=100

neighborCoeff = sumOfNeighbors(obs)
neighborCoeff = neighborCoeff + np.logical_not(neighborCoeff)

neighborCoeff = obs / neighborCoeff
a[5,80]=100
b = b*obs
a = a*obs
def diffuse(a, mask, seed, n, iter, d=0.96):
	#import pdb; pdb.set_trace()
	new = a.copy()
	for i in range(iter):
		new = d*n*sumOfNeighbors(new)*mask + seed
	#new = d*n*new*mask
	#new = new + seed
	return new

import time
a[23,50]=100
seed = a.copy()
mask = np.logical_not(seed)


t1=time.time()
a1 = diffuse(a, mask, seed, neighborCoeff, iter = 100, d=0.96)
	#b = diffuse(b, mask, seed, neighborCoeff, obs, d = 0.5)
	#print a[49:52,49:52]
t2 = time.time()
from matplotlib.colors import LogNorm, Colormap

plt.subplot(221)
imgplt = plt.imshow(a1,interpolation='none', norm=LogNorm())
plt.colorbar()
plt.title('2 cells with value 100\n100 itersions')
imgplt2 = plt.contour(a1,norm=LogNorm(),colors='black', linewidth=.5)
#implt = plt.plot_surface(a)

print "Time: %0.8f"%(t2-t1)

seed[23,50]=0
mask = np.logical_not(seed)
a2 = diffuse(a1, mask, seed, neighborCoeff, iter = 100, d=0.96)
plt.subplot(222)
imgplt = plt.imshow(a2,interpolation='none', norm=LogNorm())
plt.colorbar()
plt.title('One cell set to 0\n100 more iterations')
imgplt2 = plt.contour(a2,norm=LogNorm(),colors='black', linewidth=.5)

#implt = plt.plot_surface(a)

a3 = diffuse(a2, mask, seed, neighborCoeff, iter = 100, d=0.96)
plt.subplot(223)
imgplt = plt.imshow(a3,interpolation='none', norm=LogNorm())
plt.colorbar()
plt.title('200 iterations since set to 0')
imgplt2 = plt.contour(a3,norm=LogNorm(),colors='black', linewidth=.5)

a4 = diffuse(a3, mask, seed, neighborCoeff, iter = 100, d=0.96)
plt.subplot(224)
imgplt = plt.imshow(a4,interpolation='none', norm=LogNorm())
plt.colorbar()
plt.title('300 iterations since set to 0')
imgplt2 = plt.contour(a4,norm=LogNorm(),colors='black', linewidth=.5)
#plt.suptitle('Decay of diffusion values')
plt.show()
print "Time: %0.8f"%(t2-t1)

print a[23,50]
print a1[23,50]
print a2[23,50]
print a3[23,50]
print a4[23,50]