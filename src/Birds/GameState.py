import numpy as np
from random import randint

from EntityGroup import EntityGroup
from Entity import Entity
from Metric import Metric
from Frame import Cell

class GameState():
	"""This is the top level class responsible for managing game state"""
	entityGroups={}		#:dictionary of entity groups keyed by group name
                                            
	def __init__(self, mapFile):
		"""Constructs a new GameState object"""
                # load obstacle array from map file
                Metric.obstacleAry = np.loadtxt(mapFile, dtype='c').astype('float')
                # how many columns and rows are in this map?  (it is assumed that maps are rectangular)
                # instantiate EntityGroups
                self.entityGroups["Bird"] = EntityGroup(self, "Bird", [Metric("attract",  0.3, 30),
                                                                       Metric("repulse", -0.1, 30)])
                self.entityGroups["Food"] = EntityGroup(self, "Food", [Metric("attract",  0.5, 30)])

        def initBirds(self):
            self.entityGroups["Bird"].initBirds()
            
        def getDimensions(self):
            return Metric.obstacleAry.shape[0], Metric.obstacleAry.shape[1]
                
        def randomPosition(self):
            while True:
                discretePos = (randint(0, Metric.obstacleAry.shape[0] - 1),
                           randint(0, Metric.obstacleAry.shape[1] - 1))
                pos = (discretePos[0]*Cell.width, discretePos[1]*Cell.height)
                if not self.occupied(pos) and Metric.obstacleAry[discretePos]:
                    break
                    
            return pos
            
	def update(self):
		"""Applies diffusion to all environment metrics.  Also calls update on all entity groups"""
		for entityGroup in self.entityGroups.itervalues():
                    entityGroup.update()

	def getAllUpdatedEntities(self):
            """Returns a list of Entity objects whose states were updated as a result of the last call to update."""
            pass #TODO: waiting on EntityGroup.getUpdatedEntities

        def getGroups(self):
            """Returns a view into all entity groups"""
            return self.entityGroups.itervalues()
            
	def positionToDiscrete(self, position):
            """Convert a continuous position given by position into discrete cells"""
            return (position[0] / Cell.width, position[1] / Cell.height)

	def addEntity(self, entity, groupName):
            """Add the given entity to the group given by groupName"""
            self.entityGroups[groupName].addEntity(entity)

	def removeEntity(self, entity, groupName):
            """Remove the givent entity from the group given by groupName"""
            self.entityGroups[groupName].removeEntity(entity)

        def occupied(self, pos):
            """If any entity object is occupying the discrete cell which contains the given position,
            return True, else return False"""
            discretePosition = self.positionToDiscrete(pos)
            for entityGroup in self.entityGroups.itervalues():
                for entity in entityGroup.sprites():
                    if self.positionToDiscrete(entity.position) == discretePosition:
                        return True

            return False

	def getEntitiesAtPosition(self, position):
            """Returns a list of Entity objects who are occupying the discrete cell which contains
            the given position."""
            entitiesAtPosition = [] # list to hold all entities at the given position
            discretePosition = self.positionToDiscrete(position)
            for entityGroup in self.entityGroups.itervalues():
                for entity in entityGroup.sprites():
                    if self.positionToDiscrete(entity.position) == discretePosition:
                        entitiesAtPosition.append(entity)
                                                        
            return entitiesAtPosition

