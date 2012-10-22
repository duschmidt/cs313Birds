from pygame.sprite import Sprite

class Entity(Sprite):
	"""This is a base class for game entities"""
	gameState = None	#:reference to master game state object
	position = []		#:tuple to track position of this entity
	entityId = 0		#:some meaningful identifier for this entity

	def __init__(self, gameState, entityId):
		"""Constructs a new entity object"""
		Sprite.__init__(self)		#initialize base class
		self.gameState = gameState
		self.entityId = entityID

	def update(self):
		"""Abstract method to be overridden by inherited classes.
		   Updates entity state through interactions with gameState object"""
		raise Exception("Method must be overridden")

