try:
	import _tkinter
except(ImportError):
	print "It appears that your current version of python does not include Tkinter. Tkinter is included in standard python distributions but is sometimes removed from some custom python distributions as my have been included by default with your operating system.  To use this package please either install the tkinter package or install a full, standard version of python as can be downloaded from python.org"
	sys.exit(1)

import MapFrame as mf 
import numpy as np

ary = np.zeros((40, 40))

mainFrame = mf.MapFrame(ary)
while True:
    mainFrame.drawFrame()
mainFrame.mainLoop()
