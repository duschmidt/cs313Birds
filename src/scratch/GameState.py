import Tkinter as tk
import numpy as np
import Image
import ImageTk
import diffuse
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Colormap
from random import randint
from math import fabs

moves = [(-1,-1), (-1,0), (-1,1),
		 (0, -1),(0,0),(0,1),
		 (1, -1),(1,0),(1,1)]
noneNeighborhood = np.empty((3,3),dtype=object)


gameData = None

def sumOfNeighbors(a):
		new = np.zeros(a.shape)
		new = np.roll(a,1,0)+np.roll(a,1,1)+np.roll(a,-1,0)+np.roll(a,-1,1)
		return new

class Entity():
	"""This class represents a game entity which can interact with environment metrics and other entities"""
	atoms = {}
	def __init__(self, size, name):
		"""
			This constructor builds an entity

			@param size: a two tuple of the form (height, width) which specifies the size of this entities icon on the game map
			@param name: A string value indicating the type of entitiy.  Must be a key in the gameData['Entities'] dictionary
		"""
		self.alive = True #a boolean to indicate whether this entity is alive
		self.name = name #a name for the type of entity, used as a key into the game data structure
		self.canvasItemId = -1 #the integer identifier of a tkinter canvas item corresponding to this entity
		self.skill = 10 #a general metric for the skill level of an entity

		#Load the image file for this entity
		im = Image.open(gameData['Entities'][self.name]['Image']) 
		im = im.resize(size)
		self.image = ImageTk.PhotoImage(image=im)

		atomsNeeded = []

		#need to create atoms for layers which are both read and affected
		for weighted in gameData['Entities'][self.name]['Weights'].keys():#loop over affected layers
			#if affected layer is one that is also read
			if weighted in gameData['Entities'][self.name]['Affects'].keys():
				#need to create an atom for this layer
				
				if not Entity.atoms.has_key(self.name):
					Entity.atoms[self.name] = {}

				if not Entity.atoms[self.name].has_key(weighted):
					print "Creating atom %s %s"%(self.name, weighted)
					span = gameData['Metrics'][weighted]['iters']#how far does this layer spread in a frame
					rate = gameData['Metrics'][weighted]['rate']
					seed = np.zeros((span*2 +1,span*2+1)) #atom should consider the weighted area per frame
					mask = np.ones((span*2 +1,span*2+1))
					neighborCoeff = np.zeros((span*2+1, span*2+1))
					neighborCoeff.fill(0.25)
					diff = np.zeros((span*2 +1,span*2+1)) #atom should consider the weighted area per frame
					seed[span,span] = gameData['Entities'][self.name]['Affects'][weighted]
					mask[span,span] = 0
					for i in range(span):
						diff = rate*neighborCoeff*sumOfNeighbors(diff)*mask + seed
					Entity.atoms[self.name][weighted] = diff[span-1:span+2,span-1:span+2]
			else:
				if not Entity.atoms.has_key(self.name):
					Entity.atoms[self.name] = {}
				Entity.atoms[self.name][weighted] = np.zeros((3,3))


	def getMove(self, neighborhood):
		if not gameData['Entities'][self.name]['Moves']:
			return(0,0)

		a = np.zeros((3,3))

		for k, v in gameData['Entities'][self.name]['Weights'].items():
			a += v*(neighborhood[k]-Entity.atoms[self.name][k])

		a *= neighborhood['obstacles']
		a *= np.equal(noneNeighborhood,neighborhood['entities'])
		maxAt = np.argmax(a)
		minAt = np.argmin(a)
		max = np.max(a)
		min = np.min(a)
		moveIdx = 4

		if fabs(max) > fabs(min): #pursue max
			moveIdx = maxAt
		else: #flee min
			moveIdx = abs(minAt - 8)

		coords = np.nonzero(neighborhood['entities'])
		for row, col in zip(coords[0], coords[1]):
			if neighborhood['entities'][row,col].name in gameData['Entities'][self.name]['Eats']:
				self.skill += neighborhood['entities'][row,col].skill
				neighborhood['entities'][row,col] = None
				move = (row-1,col-1)
				return move

		move = moves[moveIdx]
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
		self.paused = True
		plt.ion()
		self.showPlot = False
		self.plotVal = "FoodMetric"
		self.height=height
		self.width=width
		self.loadMap(mapFile = "map1.map")
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
		global gameData
		dataFile = mapFile.replace('.map','.data')
		f = open(dataFile)
		gameData = eval(f.read())
		f.close()

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
		neighborCoeff = self.sumOfNeighbors(self.obstacles)#compute count of neighbor cells, where obstacles don't count
		self.neighborCoeff = neighborCoeff + np.logical_not(neighborCoeff)#neighborCoeff will be a denominator under obstacles, need to make 0's into 1's
		self.neighborCoeff = self.obstacles / self.neighborCoeff#compute the neighborCoeff, zero at obstacles
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
		self.seedMetrics()
		self.diffuseMetrics()
		coords = np.nonzero(self.entities)
		newEntities = np.empty(self.shape,dtype=object)
		for row, col in zip(coords[0], coords[1]):
			if self.entities[row,col] == None or not self.entities[row,col].alive :
				continue
			n = self.getNeighborhood(row,col)
			move = self.entities[row,col].getMove(n)
			newPos = ((row+move[0])%self.entities.shape[0], (col+move[1])%self.entities.shape[1])
			
			if self.obstacles[newPos] == 1 and (newEntities[newPos] == None or newEntities[newPos].alive==False):
				newEntities[newPos] = self.entities[row, col]
			else:
				newEntities[row,col] = self.entities[row, col]
			# 	self.entities[row,col] = None
		self.entities = newEntities
		if self.showPlot: self.plot()
		self.draw()

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
		plt.figure(0)
		plt.clf()
		plt.suptitle(self.plotVal)
		m = None
		if self.plotVal == "All":
			m = np.zeros(self.shape)
			for k, v in self.metrics.items():
				m += v['diffused']
		else:
			m = self.metrics[self.plotVal]['diffused']
		ln = LogNorm()
		plt.imshow(m,interpolation='none', norm=ln)
		plt.contour(m,norm=ln,colors='black', linewidth=.5)
		plt.show()

	def leftClick(self, event):
		row, col = self.pixelToCell(event.x, event.y)
		if self.entities[row, col] == None and gameData['InsertEntity'][0]['count'] > 0:
			self.entities[row,col] = Entity(self.cellsize, gameData['InsertEntity'][0]['entity'])
			img = self.Surface.create_image(self.cellToPixel(row,col), image=self.entities[row,col].image, anchor="nw")
			self.entities[row,col].canvasItemId = img
			gameData['InsertEntity'][0]['count'] -= 1
			if gameData['InsertEntity'][0]['count'] == 0:
					print("Out of %s"%gameData['InsertEntity'][0]['entity'])
				
	def keyPress(self, event):
		if event.char == "p":
			self.paused = not self.paused
			if not self.paused:
				self.update()
		elif event.char == "t":
			self.showPlot = not self.showPlot
			if self.showPlot:
				self.plot()
		elif event.char == "f":
			self.plotVal = "FoodMetric"
			self.plot()
		elif event.char ==  "b":
			self.plotVal = "BirdMetric"
			self.plot()
		elif event.char == "h":
			self.plotVal = "HawkMetric"
			self.plot()
		elif event.char == "a":
			self.plotVal = "All"
			self.plot()
		elif event.char == "s":
			self.paused = True
			self.update()



	def rightClick(self, event):
		row, col = self.pixelToCell(event.x, event.y)
		if self.entities[row, col] == None and gameData['InsertEntity'][1]['count'] > 0:
			self.entities[row,col] = Entity(self.cellsize, gameData['InsertEntity'][1]['entity'])
			img = self.Surface.create_image(self.cellToPixel(row,col), image=self.entities[row,col].image, anchor="nw")
			self.entities[row,col].canvasItemId = img
			gameData['InsertEntity'][1]['count'] -= 1
			if gameData['InsertEntity'][1]['count'] == 0:
				print("Out of %s"%gameData['InsertEntity'][1]['entity'])



g = Game()