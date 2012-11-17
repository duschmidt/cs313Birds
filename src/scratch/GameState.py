import Tkinter as tk
import numpy as np
import Image
import ImageTk
import diffuse
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Colormap
from random import randint

moves = [(-1,-1), (-1,0), (-1,1),
		 (0, -1),(0,0),(0,1),
		 (1, -1),(1,0),(1,1)]
noneNeighborhood = np.empty((3,3),dtype=object)


gameData = {
 'Metrics':{
 			'FoodMetric':{'rate':0.9,'iters':30},
		    'BirdMetric':{'rate':0.9,'iters':30},
		    'HawkMetric':{'rate':0.9,'iters':30}
		   },
 'Entities':{
			'Food':{ 'Eats':[],
					 'Weights':{},
					 'MapChar':'F',
					 'Image':'apple.png',
					 'Affects':{'FoodMetric':1},
					 'Moves':False
					},
			'Bird':{ 'Eats':['Food'],
					 'Weights':{
					 			'FoodMetric':1,
			   					'BirdMetric':0,
			   					'HawkMetric':0
			   					},
					 'MapChar':'B',
					 'Image':'bird.png',
					 'Affects':{'BirdMetric':1},
					 'Moves':False
					},
			'Hawk':{ 'Eats':['Bird', 'Food'],
					 'Weights':{
					 			'FoodMetric':0.5,
			   					'BirdMetric':1,
			   					'HawkMetric':0
			   					},
					 'MapChar':'H',
					 'Image':'hawk.png',
					 'Affects':{'HawkMetric':1},
					 'Moves':True
					}
			},
 'InsertEntity':'Food'
}

class Entity():
	def __init__(self, size, name):
		self.alive = True
		self.name = name
		self.canvasItemId = -1
		self.skill = 10
		im = Image.open(gameData['Entities'][self.name]['Image'])
		im = im.resize(size)
		self.image = ImageTk.PhotoImage(image=im)
	def getMove(self, neighborhood):
		if not gameData['Entities'][self.name]['Moves']:
			return(0,0)

		a = np.zeros((3,3))
		
		for k, v in gameData['Entities'][self.name]['Weights'].items():
			a += v*neighborhood[k]

		a *= neighborhood['obstacles']
		a *= np.equal(noneNeighborhood,neighborhood['entities'])
		maxAt = np.argmax(a)


		coords = np.nonzero(neighborhood['entities'])
		for row, col in zip(coords[0], coords[1]):
			if neighborhood['entities'][row,col].name in gameData['Entities'][self.name]['Eats']:
				#self.skill += neighborhood['entities'][row,col].skill
				neighborhood['entities'][row,col] = None
				move = (row-1,col-1)

		move = moves[maxAt]
		if move[0] == 0 and move[1] == 0:
			move = (randint(-1,1),randint(-1,1))

		return move

	def getMetrics(self):
		return gameData['Entities'][self.name]['Affects']

class Game(tk.Frame):
	def __init__(self, master=tk.Tk(), height=900, width=900):
		tk.Frame.__init__(self, master)
		self.master = master
		self.deltaT = 1 #:Time delay in ms between frame updates, not guaranteed
		self.paused = False
		plt.ion()
		self.showPlot = False
		self.plotVal = "FoodMetric"
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
		entityIDMapping = {}
		for k, v in gameData['Entities'].items():
			entityIDMapping[v['MapChar']] = k

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
				elif gameMap[row,col] != '.':

					self.entities[row,col] = Entity(self.cellsize, entityIDMapping[gameMap[row,col]])

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
		self.metrics = {}
		for k,v in gameData['Metrics'].items():
			self.metrics[k] = v
			self.metrics[k]['seed'] = np.zeros(self.shape)
			self.metrics[k]['diffused'] = np.zeros(self.shape)
		
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
			self.entities[row,col] = Entity(self.cellsize, gameData['InsertEntity'])
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
			self.plotVal = "FoodMetric"
		elif event.char ==  "b":
			self.plotVal = "BirdMetric"
		elif event.char == "h":
			self.plotVal = "HawkMetric"


	def rightClick(self, event):
		self.paused = not self.paused
		self.draw()


g = Game()