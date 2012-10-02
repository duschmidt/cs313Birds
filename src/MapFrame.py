from Tkinter import Frame, Tk, Menu, Canvas
import Tkinter as tkinter
import numpy as np
import scipy.signal as sig
import random as rand
from Bird import Bird

numBirds = 8 # number of birds in the map
goalProb = 0.005 # the probability that new food will appear
deltaT = 1 # time per frame in ms
diffuseAmt = 0.5 # diffusion constant - lower == less diffusion
# diffusion kernel
diffusionKernel = np.array([[diffuseAmt, diffuseAmt,  diffuseAmt],
                            [diffuseAmt, 1,           diffuseAmt],
                            [diffuseAmt, diffuseAmt,  diffuseAmt]])

class Cell:
    col = 0
    row = 0
    rect = None
    
    def __init__(self, col, row, rect):
        self.col = col
        self.row = row
        self.rect = rect
        
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row
        
class MapFrame(Frame):
        # width / height of canvas in pixels
	canvasWidth = 400
	canvasHeight = 400
        cells = []
        birds = [] # list of birds in the map
        goals = [] # list of goal cells
        
	def __init__(self, diffusionAry, master = Tk()):
            Frame.__init__(self, master = master)
            self.master = master
            self.master.title("Diffusion Map Display")
            
            self.createWidgets()
            self.pack()
            self.diffusionAry = diffusionAry
            # number of rows/ cols of cells in grid
            self.numCols = diffusionAry.shape[0]
            self.numRows = diffusionAry.shape[1]
            # width / height of canvas in pixels
            self.cellWidth  = self.canvasWidth / float(self.numCols)
            self.cellHeight = self.canvasHeight / float(self.numRows)

            self.initCells()
            self.initGoals()
            for i in range(numBirds):
                self.birds.append(Bird(self))
                    
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

        def occupied(self, cell):
            """Returns true if a bird is occupying the cell at x, y.  Returns false otherwise"""
            for bird in self.birds:
                if bird.cell == cell:
                    return True
            return False
            
	def dummy(self):
            pass

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
            return -1 if self.occupied(cell) else self.diffusionAry[cell.col, cell.row]
            
        def pointToCell(self, x, y):
            """Convert a pixel x, y point to a cell row, col pair"""
            return self.cells[(int)(x / self.cellWidth)][(int)(y / self.cellHeight)]
            
        def leftClick(self, event):
            """Left click adds/removes goal objects from the grid"""
            cell = self.pointToCell(event.x, event.y)
            if cell in self.goals:
                self.goals.remove(cell)
            else:
                self.goals.append(cell)
                
        def createCell(self, col, row, color):
            """Returns a cell at (col, row), filled with specified color"""
            x1 = col * self.cellWidth
            y1 = (row + 1) * self.cellHeight
            x2 = (col + 1) * self.cellWidth
            y2 = row * self.cellHeight
            return Cell(col, row, self.Surface.create_rectangle(x1, y1, x2, y2, fill=color))

        def initCells(self):
            for col in xrange(self.numCols):
                self.cells.append([])
                for row in xrange(self.numRows):
                    self.cells[col].append(self.createCell(col, row, "#FFFFFF"))

        def initGoals(self):
            """Populate the map randomly with goals"""
            for col in xrange(self.numCols):
                for row in xrange(self.numRows):
                    if rand.random() < goalProb:
                        self.goals.append(self.cells[col][row])

        def seedDiffusion(self):
            """Set all cells which hold goals to a max diffusion value of 1 and all other cells to 0"""
            self.diffusionAry.fill(0)
            for cell in self.goals:
                self.diffusionAry[cell.col, cell.row] = 1
                
        #Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
        def diffuse(self, numDiffusions):
            for i in xrange(numDiffusions):
                # mode='same' means the output array should be the same size
                # bounary='wrap' means to wrap the convolution around the array dimensions
                self.diffusionAry = sig.convolve2d(self.diffusionAry, diffusionKernel, mode='same', boundary='wrap')
                # convolution is unbounded, so scale the array to range [0, 1]
            max = np.max(self.diffusionAry)
            if max != 0:
                self.diffusionAry /= np.max(self.diffusionAry)
            
	def getColor(self, cell):
            return "#%02XFFFF" % int(abs(255 * (1 - self.diffusionAry[cell.col, cell.row])))
                
	def drawGrid(self):
            """Draws all the cells in the grid with an appropriate color"""
            for cellList in self.cells:
                for cell in cellList:
                    self.Surface.itemconfig(cell.rect, fill=self.getColor(cell))

        def drawBirds(self):
            for bird in self.birds:
                bird.move()
                self.Surface.itemconfig(bird.cell.rect, fill="#00FF00")

        def drawGoals(self):
            for goal in self.goals:
                self.Surface.itemconfig(goal.rect, fill="#FF0000")
                
        def drawFrame(self):
            """Main draw method, to be called every frame"""
            #self.Surface.after(deltaT)
            # randomly generate a goal from time to time
            if rand.random() < goalProb * 20:
                self.goals.append(self.cells[rand.randint(0, self.numCols - 1)][rand.randint(0, self.numRows - 1)])
            self.seedDiffusion()
            self.diffuse(numDiffusions=20)
            self.drawGrid()
            self.drawBirds()
            self.drawGoals()
            self.Surface.update_idletasks()
            self.Surface.update()
            self.Surface.after(deltaT)
            self.drawFrame()