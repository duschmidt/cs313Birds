from Tkinter import Frame, Tk, Menu, Canvas
import Tkinter as tkinter
import numpy as np
import scipy.signal as sig

class MapFrame(Frame):
	canvasWidth = 200
	canvasHeight = 200

	def __init__(self, npAry, master = Tk()):
		""""""

		Frame.__init__(self, master = master)
		self.master = master
		self.master.title("Diffusion Map Display")

		self.createWidgets()
		self.pack()
		self.npAry = npAry
		self.drawArray(npAry)

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
		#return "#FF0000"
		return "#%02XFFFF" % int(abs(255 *(1-value))%256)

	def leftClick(self, event):
		import random
		#if random.random() > 0.8:
		#	self.npAry[random.randint(0,24),random.randint(0,24)] = 1.0
		
		self.npAry = self.diffusion(self.npAry)

		#self.npAry = sig.convolve2d(np.array([[0,0.2,0],[0.2,1.0,0.2],[0,0.2,0]]),self.npAry)
		#elf.npAry = sig.convolve2d(self.npAry,np.array([[0,0.2,0],[0.2,1.0,0.2],[0,0.2,0]]))
		self.npAry[10,10]=1.0
		#sself.npAry = self.npAry + np.random.random(self.npAry.shape)
		self.drawArray(self.npAry)

	#Adapted from http://stackoverflow.com/questions/8102781/efficiently-doing-diffusion-on-a-2d-map-in-python
	def diffusion(self, arr):
		arr2 = arr.copy()
		arr2+=0.2*np.roll(arr,shift=1,axis=1) # right
		arr2+=0.2*np.roll(arr,shift=-1,axis=1) # left
		arr2+=0.2*np.roll(arr,shift=1,axis=0) # down
		arr2+=0.2*np.roll(arr,shift=-1,axis=0) # up
		return arr2
	#END ADAPTED#################################################################
	def drawArray(self, npAry):
		"""Draws the values in a 2D npAry"""
		self.Surface.delete(tkinter.ALL)
		arySize = npAry.shape
		cols = arySize[0]
		rows = arySize[1]

		xStep = self.canvasWidth / float(cols)
		yStep = self.canvasHeight / float(rows)

		for x in range(cols):
			for y in range(rows):

				color = self.getColor(npAry[x,y])
				x1 = x*xStep
				y1 = (y+1.0)*yStep
				x2 = (x+1.0)*xStep
				y2 = y*yStep
				self.Surface.create_rectangle(x1,y1,x2,y2,fill=color)
