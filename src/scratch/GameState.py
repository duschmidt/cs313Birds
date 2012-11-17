import Tkinter as tk
import numpy as np
import Image
import ImageTk
import diffuse
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Colormap
from random import randint


class Hawk():
	weights = {'Food':{'weight':0,'dir':1},
			   'Bird':{'weight':1,'dir':1},
			   'Hawk':{'weight':-0.5,'dir':1},
			   'HawkRepulse':{'weight':-0.5},
			   'BirdRepulse':{'weight':0,'dir':1}}
	def __init__(self, size):
		self.alive = True
		self.str = "H"
		self.canvasItemId = -1
		im = Image.open("hawk.png")
		im = im.resize(size)
		self.image = ImageTk.PhotoImage(image=im)
		self.skill = 1
	def getMove(self, neighborhood):
		a = np.zeros((3,3))
		for k, v in self.weights.items():
			a += v['weight']*neighborhood[k]

		maxAt = np.argmax(a)
		moves = [(-1,-1),
				 (-1,0),
				 (-1,1),
				 (0,-1),
				 (randint(-1,1),randint(-1,1)),
				 (0,1),
				 (1,-1),
				 (1,0),
				 (1,1)]
		coords = np.nonzero(neighborhood['entities'])
		for row, col in zip(coords[0], coords[1]):
			if isinstance(neighborhood['entities'][row,col],Bird):
				#global kill
				#kill = True
				#maxAt = (row,col)
				neighborhood['entities'][row,col] = None
				self.skill +=10

		return moves[maxAt]
	def getMetrics(self):
		return {'Hawk':self.skill,'HawkRepulse':2}

class Food():
	def __init__(self, size):
		self.alive = True
		self.str = "F"
		self.canvasItemId = -1
		im = Image.open("apple.png")
		im = im.resize(size)
		self.image = ImageTk.PhotoImage(image=im)
	def getMove(self, neighborhood):
		return (0,0)
	def getMetrics(self):
		return {'Food':10}

class Bird():
	weights = {'Food':{'weight':2,'dir':1},
			   'Bird':{'weight':0.5,'dir':1},
			   'Hawk':{'weight':-1,'dir':1},
			   'BirdRepulse':{'weight':-0.02,'dir':1}}
	def __init__(self, size):
		self.alive = True
		self.str = "B"
		self.canvasItemId = -1
		self.skill = 10
		im = Image.open("bird.png")
		im = im.resize(size)
		self.image = ImageTk.PhotoImage(image=im)
	def getMove(self, neighborhood):
		a = np.zeros((3,3))
		for k, v in self.weights.items():
			a += v['weight']*neighborhood[k]

		maxAt = np.argmax(a)
		moves = [(-1,-1),
				 (-1,0),
				 (-1,1),
				 (0,-1),
				 (randint(-1,1),randint(-1,1)),
				 (0,1),
				 (1,-1),
				 (1,0),
				 (1,1)]
		coords = np.nonzero(neighborhood['entities'])
		for row, col in zip(coords[0], coords[1]):
			if isinstance(neighborhood['entities'][row,col],Food):
				#global kill
				#kill = True
				#maxAt = (row,col)
				neighborhood['entities'][row,col] = None
				self.skill +=10

		return moves[maxAt]

	def getMetrics(self):
		return {'Bird':self.skill,'BirdRepulse':2}

class Game(tk.Frame):
	def __init__(self, master=tk.Tk(), height=900, width=900):
		tk.Frame.__init__(self, master)
		self.master = master
		self.deltaT = 1 #:Time delay in ms between frame updates, not guaranteed
		self.paused = False
		plt.ion()
		self.showPlot = False
		self.plotVal = "Food"
		self.height=height
		self.width=width
		self.loadMap()
		self.createWidgets()
		self.pack()
		self.initEntities()
		self.initObstacles()
		self.initMetrics()
		self.update()
		#self.plot()
		self.draw()

	def createWidgets(self):
		self.Surface = tk.Canvas(self, width=self.width, height = self.height, bg="#FFFFFF")
		self.Surface.bind("<Button-1>", self.leftClick)
		self.Surface.bind("<Button-3>", self.rightClick)
		self.master.bind("<Key>",self.keyPress)
		self.Surface.pack()

	def loadMap(self, mapFile='map1.map'):
		noneFunc = lambda size: None
		entityIDMapping = {'E':noneFunc,'F':Food,'B':Bird,'H':Hawk}
		gameMap = np.loadtxt(mapFile,dtype='c')
		self.shape = gameMap.shape
		self.entities = np.empty(gameMap.shape,dtype=object)
		self.obstacles = np.ones(gameMap.shape)
		self.cellsize = self.cellToPixel(1,1)
		self.cellsize = (int(self.cellsize[0]), int(self.cellsize[1]))
		for row in range(self.shape[0]):
			for col in range(self.shape[1]):
				if gameMap[row,col] == 'O':
					self.obstacles[row,col] = 0
				else:
					self.entities[row,col] = entityIDMapping[gameMap[row,col]](self.cellsize)

	def cellToPixel(self, row, col):
		"""Returns tuple (x,y) representing the upper left corner of the given cell in pixel coordinates"""
		return (col*float(self.width)/self.shape[1], row*float(self.height)/self.shape[0])

	def pixelToCell(self,x,y):
		"""returns tuple (row,col) representing the cell which contains the given x,y coordinate"""
		return (int(y*self.shape[0]/float(self.height)),int(x*self.shape[1]/float(self.width)))
	
	def initEntities(self):
		coords = np.nonzero(self.entities)
		for row, col in zip(coords[0], coords[1]):
			img = self.Surface.create_image(self.cellToPixel(row,col), image=self.entities[row,col].image, anchor="nw")
			self.entities[row,col].canvasItemId = img
		self.Surface.update()

	def initObstacles(self):
		neighborCoeff = self.sumOfNeighbors(self.obstacles)
		self.neighborCoeff = neighborCoeff + np.logical_not(neighborCoeff)
		self.neighborCoeff = self.obstacles / self.neighborCoeff
		coords = np.nonzero(np.logical_not(self.obstacles))
		for row, col in zip(coords[0], coords[1]):
			self.Surface.create_rectangle(self.cellToPixel(row,col), self.cellToPixel(row+1,col+1), fill="#000000")
		self.Surface.update()

	def initMetrics(self):
		self.metrics={'Hawk'		:{'rate':0.9,'iters':30,'seed':np.zeros(self.shape),'diffused':np.zeros(self.shape)},
					  'HawkRepulse' :{'rate':0.1,'iters':30,'seed':np.zeros(self.shape),'diffused':np.zeros(self.shape)},
					  'Bird'		:{'rate':0.9,'iters':30,'seed':np.zeros(self.shape),'diffused':np.zeros(self.shape)},
					  'BirdRepulse' :{'rate':0.1,'iters':30,'seed':np.zeros(self.shape),'diffused':np.zeros(self.shape)},
					  'Food'		:{'rate':0.9,'iters':30,'seed':np.zeros(self.shape),'diffused':np.zeros(self.shape)}}
		

	def seedMetrics(self):
		for name, data in self.metrics.items():
			self.metrics[name]['seed'].fill(0)
		coords = np.nonzero(self.entities)
		for row, col in zip(coords[0], coords[1]):
			entMetrics = self.entities[row,col].getMetrics()
			for k,v in entMetrics.items():
				self.metrics[k]['seed'][row,col] = v

	def diffuseMetrics(self):
		for name, data in self.metrics.items():
			seed = data['seed']
			rate = data['rate']
			itr = data['iters']
			diff = data['diffused']
			mask = np.logical_not(seed)
			#self.metrics[name]['diffused'] = diffuse.diffuse(itr, rate,
            #                         seed, self.obstacles)
			#import pdb; pdb.set_trace()
			for i in range(itr):
				diff = rate*self.neighborCoeff*self.sumOfNeighbors(diff)*mask + seed
			self.metrics[name]['diffused']=diff
	def sumOfNeighbors(self, a):
		new = np.zeros(a.shape)
		new = np.roll(a,1,0)+np.roll(a,1,1)+np.roll(a,-1,0)+np.roll(a,-1,1)
		return new

	def getNeighborhood(self,row,col):
		neighborhood = {}
		neighborhood['entities'] = self.entities[row-1:row+2, col-1:col+2]
		neighborhood['obstacles'] = self.obstacles[row-1:row+2, col-1:col+2]
		for layer, data in self.metrics.items():
			neighborhood[layer] = data['diffused'][row-1:row+2, col-1:col+2]
			if neighborhood[layer].shape != (3,3):
				print row, col
		return neighborhood

	def update(self):
		#self.initMetrics()
		self.seedMetrics()
		self.diffuseMetrics()
		coords = np.nonzero(self.entities)
		global kill
		for row, col in zip(coords[0], coords[1]):
			if self.entities[row,col] == None or not self.entities[row,col].alive :
				continue
			n = self.getNeighborhood(row,col)
			move = self.entities[row,col].getMove(n)
			newPos = ((row+move[0])%self.entities.shape[0], (col+move[1])%self.entities.shape[1])
			
			if self.obstacles[newPos] == 1 and (self.entities[newPos] == None or self.entities[newPos].alive==False):
				self.entities[newPos] = self.entities[row, col]
				self.entities[row,col] = None
			#if kill:
			#	pass#self.paused=True
		if self.showPlot: self.plot()
		self.draw()
		#plt.draw()

	def draw(self):
		coords = np.nonzero(self.entities)
		for row, col in zip(coords[0], coords[1]):
			item = self.entities[row,col].canvasItemId
			pos = self.cellToPixel(row,col)
			self.Surface.coords(item, pos)
		self.Surface.update()
		if not self.paused:
			self.Surface.after(self.deltaT,self.update)
		

	def plot(self):
		#if self.plt = None:
		plt.figure(0)
		plt.clf()

		plt.suptitle(self.plotVal)
		m = self.metrics[self.plotVal]['diffused']
		#import pdb; pdb.set_trace()
		#lmin = np.min(m)
		#from math import fabs
		#n = fabs(lmin)*np.ones(m.shape)
		ln = LogNorm()
		#m = n + m
		#ln.autoscale(m)
		plt.imshow(m,interpolation='none', norm=ln)
		plt.contour(m,norm=ln,colors='black', linewidth=.5)
		#plt.imshow(m,interpolation='none')
		#plt.contour(m,colors='black', linewidth=.5)
		#plt.canvas.draw()
		plt.show()

	def leftClick(self, event):
		row, col = self.pixelToCell(event.x, event.y)
		if self.entities[row, col] == None:
			self.entities[row,col] = Food(self.cellsize)
			img = self.Surface.create_image(self.cellToPixel(row,col), image=self.entities[row,col].image, anchor="nw")
			self.entities[row,col].canvasItemId = img
		# if self.paused:
		# 	self.update()
			
		# 	fCount = 0
		# 	for Name, data in self.metrics.items():
		# 		pass
				
	def keyPress(self, event):
		print "KeyPress"
		if event.char == "p":
			self.showPlot = not self.showPlot
		elif event.char == "f":
			self.plotVal = "Food"
		elif event.char ==  "b":
			self.plotVal = "Bird"
		elif event.char == "h":
			self.plotVal = "Hawk"


	def rightClick(self, event):
		self.paused = not self.paused
		self.draw()


g = Game()