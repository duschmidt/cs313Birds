import pygame
from pygame.sprite import Sprite
from pygame.rect import Rect

import os

def load_image(name, position, dims, colorkey=None):
    """Load an image located in the data directory.
        Returns an image, rect pair which Sprite uses in its draw() function.
        posidion and dims should be a tuple of the form (width, height) 
        An optional colorkey argument represents a color of the image that is transparent.
        Code adapted from http://www.pygame.org/docs/tut/chimp/ChimpLineByLine.html"""
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
    return pygame.transform.smoothscale(image, dims), Rect(position, dims)

class Entity(Sprite):
	"""This is a base class for game entities"""
	gameState = None	#:reference to master game state object
	position = []		#:tuple to track position of this entity
	entityId = 0		#:some meaningful identifier for this entity

	def __init__(self, gameState, entityId, position):
		"""Constructs a new entity object at the given position"""
		Sprite.__init__(self)		#initialize base class
		self.gameState = gameState
		self.entityId = entityId
                self.position = position

	def update(self):
		"""Abstract method to be overridden by inherited classes.
		   Updates entity state through interactions with gameState object"""
		raise Exception("Method must be overridden")

