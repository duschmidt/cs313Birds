from Tkinter import Frame, Tk, Menu, Canvas
import Tkinter as tkinter
import numpy as np
#import scipy.signal as sig
import random as rand
from Bird import Bird

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
        self.rect = Surface.create_rectangle(x1, y1, x2, y2, fill=self.whichColor(0))

    def whichColor(self, diffusionValue):
        if self.type == '0':
            return "#000000" # obstacle - black
        elif self.type == '*':
            return "#FF0000" # food - red
        else:
            # blank cell - return color based on diffusion value
            return "#%02XFFFF" % int(abs(255 * (1 - diffusionValue)))
            

    def updateColor(self, Surface, diffusionValue):
        Surface.itemconfig(self.rect, fill=self.whichColor(diffusionValue))
        
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row
        
class MapFrame(Frame):
    # width / height of canvas in pixels
    canvasWidth = 400
    canvasHeight = 400
    cells = []
    birds = [] # list of birds in the map
        
    def __init__(self, mapFileName, master = Tk()):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Diffusion Map Display")
        
        self.createWidgets()
        self.pack()
        self.loadMap(mapFileName)
        self.initGoals()
        for i in range(numBirds):
            self.birds.append(Bird(self))
                
    def dummy(self):
        """ Dummy function for menu items"""
        pass

    def stop(self):
        """Stop running the main loop"""
        self.running = False

    def createWidgets(self):
        self.menubar = Menu(self.master)
        fileMenu = Menu(self.menubar, tearoff=0)
        fileMenu.add_command(label='Export', command=self.dummy)
        fileMenu.add_command(label='Properties', command=self.dummy)
        fileMenu.add_command(label='Save', command=self.dummy)
        fileMenu.add_command(label='Open', command=self.dummy)
        fileMenu.add_command(label='Import', command=self.dummy)
        fileMenu.add_command(label='Close', command=self.stop)
        self.menubar.add_cascade(label="File", menu=fileMenu)
        self.master.config(menu=self.menubar)

        self.Surface = Canvas(self, width=self.canvasWidth, height = self.canvasHeight, bg="#FFFFFF")
        self.Surface.grid(row=0,column=0)
        self.Surface.bind("<Button-1>", self.leftClick)

    def initCells(self, mapEncoding):
        for col in xrange(self.numCols):
            self.cells.append([])
            for row in xrange(self.numRows):
                self.cells[col].append(Cell(self.Surface, col, row, mapEncoding[col, row]))


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

    def occupied(self, cell):
        """Returns true if a bird is occupying the cell at x, y.  Returns false otherwise"""
        for bird in self.birds:
            if bird.cell == cell:
                return True
        return False

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

    def valueInDirection(self, cell, direction):
        cell = self.cellInDirection(cell, direction)
        if self.occupied(cell) or cell.type == '0':
            return -1
        elif cell.type == '*': # goal type
            return 100
        else:
            return self.diffusionAry[cell.col, cell.row]

    def pointToCell(self, x, y):
        """Convert a pixel x, y point to a cell row, col pair"""
        return self.cells[(int)(x / Cell.width)][(int)(y / Cell.height)]

    def leftClick(self, event):
        """Left click adds/removes goal objects from the grid"""
        cell = self.pointToCell(event.x, event.y)
        if cell.type == '*':
            cell.type = '1'
        elif cell.type != '0':
            cell.type = '*'

    def initGoals(self):
        """Populate the map randomly with goals"""
        for col in xrange(self.numCols):
            for row in xrange(self.numRows):
                if rand.random() < goalProb:
                    self.cells[col][row].type = '*'

    def seedDiffusion(self):
        """Set all cells which hold goals to a max diffusion value of 1 and all other cells to 0"""
        self.diffusionAry.fill(0)
        for col in xrange(self.numCols):
            for row in xrange(self.numRows):
                cell = self.cells[col][row]
                if cell.type == '*':
                    self.diffusionAry[cell.col, cell.row] = 1

    def sumOfNeighbors(self, col, row):
        total = 0
        total += self.diffusionAry[col][(row - 1) % self.numRows]
        total += self.diffusionAry[col][(row + 1) % self.numRows]
        total += self.diffusionAry[(col + 1) % self.numCols][row]
        total += self.diffusionAry[(col - 1) % self.numCols][row]
        return total
            
    def manualDiffuse(self, numDiffusions):
        """Works correctly with obstacles, but is very slow"""
        for d in xrange(numDiffusions):
            for col in range(self.numCols):
                for row in range(self.numRows):
                    cell = self.cells[col][row]
                    if cell.type == '1':
                        self.diffusionAry[col][row] = diffuseAmt * self.sumOfNeighbors(col, row)

    #Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
    def diffuse(self, numDiffusions):
        for i in xrange(numDiffusions):
            # mode='same' means the output array should be the same size
            # bounary='wrap' means to wrap the convolution around the array dimensions
            #self.diffusionAry = sig.convolve2d(self.diffusionAry, diffusionKernel, mode='same', boundary='wrap')
            ary = self.diffusionAry * self.obstacleAry
            ary += (diffuseAmt*np.roll(self.diffusionAry*self.obstacleAry, 1, 0))
            ary += (diffuseAmt*np.roll(self.diffusionAry*self.obstacleAry, -1, 0))
            ary += (diffuseAmt*np.roll(self.diffusionAry*self.obstacleAry, 1, 1))
            ary += (diffuseAmt*np.roll(self.diffusionAry*self.obstacleAry, -1, 1))
            self.diffusionAry = ary
        # convolution is unbounded, so scale the array to range [0, 1]
        max = np.max(self.diffusionAry)
        if max > 0:
            self.diffusionAry /= max
                            
    def drawGrid(self):
            """Fills all the cells in the grid with an appropriate color"""
            for cellList in self.cells:
                for cell in cellList:
                    max = np.max(self.diffusionAry)
                    if max:
                        scaled = self.diffusionAry[cell.col, cell.row] / max
                    else:
                        scaled = 0
                    cell.updateColor(self.Surface, scaled)

    def drawBirds(self):
        for bird in self.birds:
            bird.move()
            self.Surface.itemconfig(bird.cell.rect, fill="#00FF00")
                
    def drawFrame(self):
        """Main draw method, to be called every frame"""
        #self.Surface.after(deltaT)
        # randomly generate a goal from time to time
        if rand.random() < goalProb * 20:
            cell = self.cells[rand.randint(0, self.numCols - 1)][rand.randint(0, self.numRows - 1)]
            if cell.type != '0':
                cell.type = '*'
        self.seedDiffusion()
        self.diffuse(numDiffusions=50)
        self.drawGrid()
        self.drawBirds()
        self.Surface.update_idletasks()
        self.Surface.update()

    def mainloop(self):
        self.running = True
        while self.running:
            # draw frame every deltaT ms
            self.Surface.after(deltaT)
            self.drawFrame()