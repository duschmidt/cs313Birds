from Tkinter import *
import Tkinter as tkinter
import numpy as np
#import scipy.signal as sig
import random as rand
from Bird import Bird
import math

numBirds = 8 # number of birds in the map
goalProb = 0.005 # the probability that new food will appear
deltaT = 0 # time per frame in ms
diffuseAmt = 0.2 # diffusion constant - lower == less diffusion
# diffusion kernel
diffusionKernel = np.array([[diffuseAmt, diffuseAmt,  diffuseAmt],
                            [diffuseAmt, 1,           diffuseAmt],
                            [diffuseAmt, diffuseAmt,  diffuseAmt]])

class Cell:
    col = 0
    row = 0
    color = "#FFFFFF"
    rect = None
    width = 0
    height = 0
    
    def __init__(self, Surface, col, row, type):
        x1 = col * self.width
        y1 = (row + 1) * self.height
        x2 = (col + 1) * self.width
        y2 = row * self.height

        self.col = col
        self.row = row
        self.type = type
        self.rect = Surface.create_rectangle(x1, y1, x2, y2, fill=self.whichColor(0,100))
        self.text = Surface.create_text((x1+x2)/2.0,(y1+y2)/2.0, text = '0')
    def whichColor(self, diffusionValue, maxValue):
        if self.type == '0':
            return "#000000" # obstacle - black
        elif self.type == '*':
            return "#FF0000" # food - red
        else:
            # blank cell - return color based on diffusion value
            val = 0
            try:
                val = diffusionValue / float(maxValue)
                if math.isnan(val): val=0
            except:
                val = 0
            return "#%02XFFFF" % int(abs(255 * (1 - val)))
            

    def updateColor(self, Surface, diffusionValue, maxValue):
        Surface.itemconfig(self.rect, fill=self.whichColor(diffusionValue, maxValue))
        Surface.itemconfig(self.text, text=str(diffusionValue))
        
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row
        
class MapFrame(Frame):
    # width / height of canvas in pixels
    canvasWidth = 800
    canvasHeight = 800
    cells = []
    birds = [] # list of birds in the map
        
    def __init__(self, mapFileName, master = Tk()):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Diffusion Map Display")
        
        self.createWidgets()
        self.pack()

        #The loadMap and initGoals can be performed in the Map object constructor
        self.loadMap(mapFileName)
        self.initGoals()


        for i in range(numBirds):
            self.birds.append(Bird(self))
    

    def createWidgets(self):
        def dummy():
            """ Dummy function for menu items"""
            pass

        def pause():
            """Pause the main loop"""
            self.paused = not self.paused
            self.runMenu.entryconfig(1, state=ACTIVE) # enable step

        def step(event=None):
            """Step forward one frame.  Only available when paused"""
            if self.paused:
                self.drawFrame()

        def stop():
            """Stop running the main loop"""
            self.running = False
        
        def leftClick(event):
            """Left click adds/removes goal objects from the grid"""
            cell = self.pointToCell(event.x, event.y)
            if cell.type == '*':
                cell.type = '1'
            elif cell.type != '0':
                cell.type = '*'

        def beginRightClick(event):
            """Right Click shows diffusion val for the clicked cell"""
            cell = self.pointToCell(event.x, event.y)
            self.currText = self.Surface.create_text(event.x, event.y, anchor=W, text="Diff Val = " + str(self.diffusionAry[cell.col, cell.row]))

        def endRightClick(event):
            self.Surface.delete(self.currText)
        
        menubar = Menu(self.master)
        fileMenu = Menu(menubar, tearoff=0)
        runMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label='Export', command=dummy)
        fileMenu.add_command(label='Properties', command=dummy)
        fileMenu.add_command(label='Save', command=dummy)
        fileMenu.add_command(label='Open', command=dummy)
        fileMenu.add_command(label='Import', command=dummy)
        fileMenu.add_command(label='Close', command=stop)
        runMenu.add_checkbutton(label='Pause', command=pause)
        runMenu.add_command(label='Step', command=step, state=DISABLED, accelerator="CTRL+S")
        self.bind_all("<Control-s>", step)
        menubar.add_cascade(label='File', menu=fileMenu)
        menubar.add_cascade(label='Run', menu=runMenu)
        self.master.config(menu=menubar)

        self.Surface = Canvas(self, width=self.canvasWidth, height = self.canvasHeight, bg="#FFFFFF")
        self.Surface.grid(row=0,column=0)
        self.Surface.bind("<Button-1>", leftClick)
        self.Surface.bind("<Button-3>", beginRightClick)
        self.Surface.bind("<ButtonRelease-3>", endRightClick)
    
    #Frame method that acts on Map object    
    def initCells(self, mapEncoding):
        for col in xrange(self.numCols):
            self.cells.append([])
            for row in xrange(self.numRows):
                self.cells[col].append(Cell(self.Surface, col, row, mapEncoding[col, row]))


    #Map Method, cell access can be pushed into initCells
    def loadMap(self, mapFileName):
        # load character encoding from the given map file
        mapEncoding = np.loadtxt(mapFileName, dtype='c')
        self.obstacleAry = mapEncoding.astype('float')
        # store number of rows/ cols of cells in grid
        self.numCols = mapEncoding.shape[0]
        self.numRows = mapEncoding.shape[1]
        # width / height of a single cell in pixels
        Cell.width  = self.canvasWidth / float(self.numCols)
        Cell.height = self.canvasHeight / float(self.numRows)
        # initialize diffusion array to zeros
        self.diffusionAry = np.zeros((self.numCols, self.numRows))
        self.initCells(mapEncoding)

    #Frame Method? Might be AgentGroup?  Seems to be somewhere in between
    def occupied(self, cell):
        """Returns true if a bird is occupying the cell at x, y.  Returns false otherwise"""
        for bird in self.birds:
            if bird.cell == cell:
                return True
        return False

    #Map Method, maybe a frame method?
    def cellInDirection(self, cell, direction):
        col = cell.col
        row = cell.row
        if direction == 'N':
            row -= 1
        elif direction == 'S':
            row += 1
        elif direction == 'E':
            col += 1
        else:
            col -= 1

        # wrap around grid boundaries
        col %= self.numCols
        row %= self.numRows

        return self.cells[col][row]

    #Map Method, may need modification
    def valueInDirection(self, cell, direction):
        cell = self.cellInDirection(cell, direction)
        if self.occupied(cell) or cell.type == '0':
            return -1
        #elif cell.type == '*': # goal type
        #    return 100
        else:
            return self.diffusionAry[cell.col, cell.row]

    
    #Map Method
    def pointToCell(self, x, y):
        """Convert a pixel x, y point to a cell row, col pair"""
        return self.cells[(int)(x / Cell.width)][(int)(y / Cell.height)]
    
    #Map Method
    def initGoals(self):
        """Populate the map randomly with goals"""
        for col in xrange(self.numCols):
            for row in xrange(self.numRows):
                if rand.random() < goalProb:
                    cell = self.cells[col][row]
                    if not cell.type == '0':
                        cell.type = '*'

    #Map Method
    def seedDiffusion(self):
        """Set all cells which hold goals to a max diffusion value of 1 and all other cells to 0"""
        self.diffusionAry.fill(0)
        for col in xrange(self.numCols):
            for row in xrange(self.numRows):
                cell = self.cells[col][row]
                if cell.type == '*':
                    self.diffusionAry[cell.col, cell.row] = 1

    #Map Method
    def sumOfNeighbors(self, col, row):
        total = 0
        total += self.diffusionAry[col][(row - 1) % self.numRows]
        total += self.diffusionAry[col][(row + 1) % self.numRows]
        total += self.diffusionAry[(col + 1) % self.numCols][row]
        total += self.diffusionAry[(col - 1) % self.numCols][row]
        return total
    
    #Map Method
    def manualDiffuse(self, numDiffusions):
        """Works correctly with obstacles, but is slow"""
        print "Manual"
        for d in xrange(numDiffusions):
            for col in range(self.numCols):
                for row in range(self.numRows):
                    # if the diffusion == 1, it is food. don't diffuse
                    if not self.diffusionAry[col][row] == 1:
                        self.diffusionAry[col][row] = diffuseAmt * self.sumOfNeighbors(col, row) * self.obstacleAry[col][row]

    #Map Method
    #Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
    def diffuse(self, numDiffusions):
        seed = self.diffusionAry.copy()
        ary = self.diffusionAry
        for i in xrange(numDiffusions):
            # mode='same' means the output array should be the same size
            # bounary='wrap' means to wrap the convolution around the array dimensions
            #self.diffusionAry = sig.convolve2d(self.diffusionAry, diffusionKernel, mode='same', boundary='wrap') * self.obstacleAry
            newAry = ary.copy()
            for i in (-1, 1):
                for j in (0, 1):                    
                    newAry += np.roll(ary, i, j)*self.obstacleAry
            ary = ((newAry + seed) * self.obstacleAry)
        self.diffusionAry = ary
        # convolution is unbounded, so scale the array to range [0, 1]
        # max = np.max(self.diffusionAry)
        # if max > 0:
        #     self.diffusionAry /= max
    
    #Frame method that acts on Map object             
    def drawGrid(self):
            """Fills all the cells in the grid with an appropriate color"""
            for cellList in self.cells:
                for cell in cellList:
                    max = np.max(self.diffusionAry)
                    val = self.diffusionAry[cell.col, cell.row]
                    #if max:
                    #    scaled =  / max
                    #else:
                    #    scaled = 0
                    cell.updateColor(self.Surface, val, max)

    #Frame method that acts on AgentGroup
    def drawBirds(self):
        for bird in self.birds:
            bird.move()
            self.Surface.itemconfig(bird.cell.rect, fill="#00FF00")

    #Frame Method           
    def drawFrame(self):
        """Main draw method, to be called every frame"""
        # randomly generate a goal from time to time
        if rand.random() < goalProb * 20:
            cell = self.cells[rand.randint(0, self.numCols - 1)][rand.randint(0, self.numRows - 1)]
            if cell.type != '0':
                cell.type = '*'
        self.seedDiffusion()
        #if np.max(self.diffusionAry): # are there any goals?
        self.diffuse(numDiffusions=10)
        self.drawGrid()
        self.drawBirds()

    #Frame Method
    def mainloop(self):
        self.running = True
        self.paused = False
        while self.running:
            # draw frame every deltaT ms
            self.Surface.after(deltaT)
            if not self.paused: # don't draw next frame if paused
                self.drawFrame()
            self.Surface.update_idletasks()
            self.Surface.update()
