import pygame
from pygame.sprite import Sprite
from pygame.rect import Rect

from Frame import Cell

import os

images = {}

def load_image(name, position, dims, colorkey=None):
    """Load an image located in the data directory.
        Returns an image, rect pair which Sprite uses in its draw() function.
        posidion and dims should be a tuple of the form (width, height) 
        An optional colorkey argument represents a color of the image that is transparent.
        Code adapted from http://www.pygame.org/docs/tut/chimp/ChimpLineByLine.html"""
    
    if name in images: # if the image has already been loaded, don't waste the time loading it again
        return images[name], Rect(position, dims)
        
    fullname = os.path.join('../../data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        emage.set_colorkey(colorkey, RLEACCEL)
    #return image, image.get_rect()
    images[name] = pygame.transform.smoothscale(image, dims)
    return images[name], Rect(position, dims)

class Entity(Sprite):
	"""This is a base class for game entities"""
	gameState = None	#:reference to master game state object
	id =    0		#:some meaningful identifier for this entity

	def __init__(self, gameState, id, position):
		"""Constructs a new entity object at the given position"""
		Sprite.__init__(self)		#initialize base class
                self.id = id
		self.gameState = gameState

                
	def update(self):
		"""Abstract method to be overridden by inherited classes.
		   Updates entity state through interactions with gameState object"""
		raise Exception("Method must be overridden")

        def position(self):
            return self.rect.topleft

        def positionInDirection(self, direction):
            currPos = self.rect.topleft
            dimensions = self.gameState.getDimensions()
            
            if direction == 'N':
                return (currPos[0], (currPos[1] - Cell.height) % dimensions[1])
            elif direction == 'S':
                return (currPos[0], (currPos[1] + Cell.height) % dimensions[1])
            elif direction == 'E':
                return ((currPos[0] + Cell.width) % dimensions[0], currPos[1])
            elif direction == 'W':
                return ((currPos[0] - Cell.width) % dimensions[0], currPos[1])
                
