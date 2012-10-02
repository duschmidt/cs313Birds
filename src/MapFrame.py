from Tkinter import Frame, Tk, Menu, Canvas
import Tkinter as tkinter
import numpy as np
import scipy.signal as sig
import random as rand

class MapFrame(Frame):
        # width / height of canvas in pixels
	canvasWidth = 400
	canvasHeight = 400
        # number of horizontal / vertical grid cells
        numCols = 0
        numRows = 0

	def __init__(self, npAry, master = Tk()):
		Frame.__init__(self, master = master)
		self.master = master
		self.master.title("Diffusion Map Display")

		self.createWidgets()
		self.pack()
		self.npAry = npAry
                self.numCols = npAry.shape[0]
                self.numRows = npAry.shape[1]
                self.initRandomSeeds()
                
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

	def dummy(self):
		pass

	def getColor(self, value):
		return "#%02XFFFF" % int(abs(255 * (1 - value)))

        def initRandomSeeds(self):
                for x in xrange(self.numCols):
                        for y in xrange(self.numRows):
                                if rand.random() < .01:
                                        self.npAry[x, y] = 1
                                        
        def leftClick(self, event):
		self.diffuse(numDiffusions=5, diffuseAmt=0.2)
		self.drawArray(self.npAry)

        #Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
        def diffuse(self, numDiffusions, diffuseAmt):
                kernel = np.array([[0,          diffuseAmt,  0         ],
                                   [diffuseAmt, 1,           diffuseAmt],
                                   [0,          diffuseAmt,  0         ]])
                for i in xrange(numDiffusions):
                        # mode='same' means the output array should be the same size
                        # bounary='wrap' means to wrap the convolution around the array dimensions
                        self.npAry = sig.convolve2d(self.npAry, kernel, mode='same', boundary='wrap')
                        # convolution is unbounded, so scale the array to range [0, 1]
                        max = np.max(self.npAry)
                        if max != 0:
                                self.npAry = self.npAry / np.max(self.npAry)
                        
	def drawArray(self, npAry):
		"""Draws the values in a 2D npAry"""
		self.Surface.delete(tkinter.ALL)
		xStep = self.canvasWidth / float(self.numCols)
		yStep = self.canvasHeight / float(self.numRows)

		for x in range(self.numCols):
			for y in range(self.numRows):
				color = self.getColor(npAry[x,y])
				x1 = x*xStep
				y1 = (y+1.0)*yStep
				x2 = (x+1.0)*xStep
				y2 = y*yStep
				self.Surface.create_rectangle(x1,y1,x2,y2,fill=color)
