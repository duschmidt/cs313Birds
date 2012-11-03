import numpy as np
from random import randint

from EntityGroup import EntityGroup
from Entity import Entity
from Metric import Metric
from Frame import Cell
from Food import Food

class GameState():
	"""This is the top level class responsible for managing game state"""
	entityGroups={}		#:dictionary of entity groups keyed by group name
                                            
	def __init__(self, mapFile):
		"""Constructs a new GameState object"""
                # load obstacle array from map file
                Metric.obstacleAry = np.loadtxt(mapFile, dtype='c').astype('double')
                # how many columns and rows are in this map?  (it is assumed that maps are rectangular)
                # instantiate EntityGroups
                self.entityGroups["Bird"] = EntityGroup(self, "Bird", [Metric("attract",  0.2, 100),
                                                                       Metric("repulse", -0.1, 100)])
                self.entityGroups["Food"] = EntityGroup(self, "Food", [Metric("attract",  0.2, 100)])

        def initBirds(self):
            self.entityGroups["Bird"].initBirds()
            
        def getDiscreteDimensions(self):
            return Metric.obstacleAry.shape[0], Metric.obstacleAry.shape[1]

        def getDimensions(self):
            discreteDimensions = self.getDiscreteDimensions()
            return discreteDimensions[0] * Cell.width, discreteDimensions[1] * Cell.height
            
        def randomPosition(self):
            while True:
                discretePos = (randint(0, Metric.obstacleAry.shape[0] - 1),
                           randint(0, Metric.obstacleAry.shape[1] - 1))
                pos = (discretePos[0]*Cell.width, discretePos[1]*Cell.height)
                if not (self.isFoodAtPosition(pos) or self.isObstacleAtPosition(pos)):
                    break
                    
            return pos
            
	def update(self):
		"""Applies diffusion to all environment metrics.  Also calls update on all entity groups"""
		for entityGroup in self.entityGroups.itervalues():
                    entityGroup.update()

        def addFood(self, position):
            self.entityGroups["Food"].add(Food(self, 0, position))
            
	def getAllUpdatedEntities(self):
            """Returns a list of Entity objects whose states were updated as a result of the last call to update."""
            pass #TODO: waiting on EntityGroup.getUpdatedEntities

        def getGroups(self):
            """Returns a view into all entity groups"""
            return self.entityGroups.values()
            
	def positionToDiscrete(self, position):
            """Convert a continuous position given by position into discrete cells"""
            return (position[0] / Cell.width, position[1] / Cell.height)
            
	def addEntity(self, entity, groupName):
            """Add the given entity to the group given by groupName"""
            self.entityGroups[groupName].addEntity(entity)

	def removeEntity(self, entity, groupName):
            """Remove the givent entity from the group given by groupName"""
            self.entityGroups[groupName].remove(entity)

        def isEntityAtPosition(self, groupName, position):
            """If any entity object of the given group type is occupying the discrete cell
            which contains the given position, return True, else return False"""
            discretePosition = self.positionToDiscrete(position)
            for entity in self.entityGroups[groupName].sprites():
                if self.positionToDiscrete(entity.position()) == discretePosition:
                    return True
                    
            return False
            
        def isBirdAtPosition(self, position):
            """If any bird is occupying the discrete cell
            which contains the given position, return True, else return False"""
            return self.isEntityAtPosition("Bird", position)

        def isFoodAtPosition(self, position):
            """If a food item is occupying the discrete cell
            which contains the given position, return True, else return False"""
            return self.isEntityAtPosition("Food", position)

        def isObstacleAtPosition(self, position):
            """If an obstacle is occupying the discrete cell
            which contains the given position, return True, else return False"""
            discretePosition = self.positionToDiscrete(position)
            return not Metric.obstacleAry[discretePosition]
            
	def getEntitiesAtPosition(self, position):
            """Returns a list of Entity objects who are occupying the discrete cell which contains
            the given position."""
            entitiesAtPosition = [] # list to hold all entities at the given position
            discretePosition = self.positionToDiscrete(position)
            for entityGroup in self.entityGroups.itervalues():
                for entity in entityGroup.sprites():
                    if self.positionToDiscrete(entity.position()) == discretePosition:
                        entitiesAtPosition.append(entity)
                                                        
            return entitiesAtPosition

