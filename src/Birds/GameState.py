from EntityGroup import EntityGroup
from Entity import Entity

class GameState():
	"""This is the top level class responsible for managing game state"""
	entityGroups={}			#dictionary of entity groups keyed by group name
	obstacleArray = None	#A numpy array for storing diffusion obstacles

	def __init__(self):
		"""Constructs a new GameState object"""
		pass

	def update(self):
		"""Applies diffusion to all environment metrics.  Also calls update on all entity groups"""
		pass

	def getAllUpdatedEntities(self):
		"""Returns a list of Entity objects whose states were updated as a result of the last call to update."""
		pass

	def positionToDiscrete(self, position):
		"""Convert a continuous position given by position into discrete cells"""
		pass

	def addEntityGroup(self, groupName, diffusionRate):
		"""Create a new entity group with the given group name and diffusion rate"""
		pass

	def removeEntityGroup(self, groupName):
		"""Remove the entity group with the given name"""
		pass

	def addEntity(self, entity, groupName):
		"""Add the given entity to the group given by groupName"""
		pass

	def removeEntity(self, entity, groupName):
		"""Remove the givent entity from the group given by groupName"""
		pass

	def getEntitiesAtPosition(self, position):
		"""Returns a list of Entity objects who are occupying the discrete cell which contains
		the given position."""
		pass


