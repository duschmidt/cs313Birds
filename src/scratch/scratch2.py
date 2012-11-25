import numpy as np

class Test():
	attr = 1
	def __init__(self, other):
		self.atter2=other
	def __str__(self):
		return "me: %d, %d"%(self.attr, self.atter2)
	def get(self):
		return self.atter2

a = np.empty((10,10), dtype=object)

a[3,3]=Test(2)
a[4,4]=Test(4)
a[5,3]=Test(5)