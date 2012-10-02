from Tkinter import Frame, Tk, Menu, Canvas
import Tkinter as tkinter
import numpy as np
import scipy.signal as sig
import random as rand
import Bird

class MapFrame(Frame):
        # width / height of canvas in pixels
	canvasWidth = 400
	canvasHeight = 400
        birds = [] # list of birds in the map
        deltaT = 1 # time per frame in ms
        goals = [] # list to hold goal positions
        diffuseAmt = 0.2
        # diffusion kernel
        kernel = np.array([[0,          diffuseAmt,  0         ],
                           [diffuseAmt, 1,           diffuseAmt],
                           [0,          diffuseAmt,  0         ]])
        
        
	def __init__(self, npAry, master = Tk()):
		Frame.__init__(self, master = master)
		self.master = master
		self.master.title("Diffusion Map Display")

		self.createWidgets()
		self.pack()
		self.npAry = npAry
                # number of rows/ cols of cells in grid
                self.numCols = npAry.shape[0]
                self.numRows = npAry.shape[1]
                # width / height of canvas in pixels
                self.cellWidth  = self.canvasWidth / float(self.numCols)
                self.cellHeight = self.canvasHeight / float(self.numRows)

                self.initGoals()
                for i in range(10):
                    self.birds.append(Bird.Bird(self))
                
	def createWidgets(self):
		self.menubar = Menu(self.master)
		fileMenu = Menu(self.menubar, tearoff=0)
		fileMenu.add_command(label='Export', command=self.dummy())
		fileMenu.add_command(label='Properties', command=self.dummy())
		fileMenu.add_command(label='Save', command=self.dummy())
		fileMenu.add_command(label='Open', command=self.dummy())
		fileMenu.add_command(label='Import', command=self.dummy())
		fileMenu.add_command(label='Close', command=self.dummy())
		self.menubar.add_cascade(label="File", menu=fileMenu)
		self.master.config(menu=self.menubar)

		self.Surface = Canvas(self, width=self.canvasWidth, height = self.canvasHeight, bg="#FFFFFF")
		self.Surface.grid(row=0,column=0)
		self.Surface.bind("<Button-1>", self.leftClick)

        def occupied(self, x, y):
            """Returns true if a bird is occupying the cell at x, y.  Returns false otherwise"""
            for bird in self.birds:
                if bird.x == x and bird.y == y:
                    return True
            return False
            
	def dummy(self):
		pass

        def pointToCell(self, x, y):
            """Convert a pixel x, y point to a cell row, col pair"""
            return [(int)(x / self.cellWidth), (int)(y / self.cellHeight)]
            
        def leftClick(self, event):
            """Left click adds/removes goal objects from the grid"""
            [x, y] = self.pointToCell(event.x, event.y)
            if [x, y] in self.goals:
                self.goals.remove([x, y])
            else:
                self.goals.append([x, y])

        def initGoals(self):
            """Populate the map randomly with goals"""
            for x in xrange(self.numCols):
                for y in xrange(self.numRows):
                    if rand.random() < .01:
                        self.goals.append([x, y])

        def seedDiffusion(self):
            """Set all cells which hold goals to a max diffusion value of 1 and all other cells to 0"""
            self.npAry.fill(0)
            for goal in self.goals:
                self.npAry[goal[0], goal[1]] = 1
                
        #Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
        def diffuse(self, numDiffusions):
                for i in xrange(numDiffusions):
                        # mode='same' means the output array should be the same size
                        # bounary='wrap' means to wrap the convolution around the array dimensions
                        self.npAry = sig.convolve2d(self.npAry, self.kernel, mode='same', boundary='wrap')
                        # convolution is unbounded, so scale the array to range [0, 1]
                        max = np.max(self.npAry)
                        if max != 0:
                                self.npAry /= np.max(self.npAry)
            
	def getColor(self, x, y):
                if [x, y] in self.goals:
                    return "#FF0000"
                else:
                    return "#%02XFFFF" % int(abs(255 * (1 - self.npAry[x,y])))

        def drawCell(self, x, y, color):
                """Draw a single cell at pos (x, y), filled with specified color"""
                x1 = x * self.cellWidth
                y1 = (y + 1) * self.cellHeight
                x2 = (x + 1) * self.cellWidth
                y2 = y * self.cellHeight
                self.Surface.create_rectangle(x1, y1, x2, y2, fill=color)
                
	def drawGrid(self):
		"""Draws all the cells in the grid with an appropriate color"""
		self.Surface.delete(tkinter.ALL)
		for x in xrange(self.numCols):
			for y in xrange(self.numRows):
                                self.drawCell(x, y, self.getColor(x, y))

        def drawBirds(self):
            for bird in self.birds:
                bird.move()
                self.drawCell(bird.x, bird.y, bird.color)
                
        def drawFrame(self):
            """Main draw method, to be called every frame"""
            #self.Surface.after(self.deltaT)
            # randomly generate a goal from time to time
            if rand.random() < .2:
                self.goals.append([rand.randint(0, self.numCols - 1), rand.randint(0, self.numRows - 1)])
            self.seedDiffusion()
            self.diffuse(numDiffusions=20)
            self.drawGrid()
            self.drawBirds()
            self.Surface.update()