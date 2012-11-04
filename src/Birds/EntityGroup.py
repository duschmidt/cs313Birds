from pygame.sprite import Group
from random import random

from Metric import Metric
from Food import Food
from Bird import Bird
from Hawk import Hawk

class EntityGroup(Group):
    """This class manages a group of entities and their diffused environment metrics"""

    gameState = None            #:Reference to global game state
    name = None		        #:A name for this group

    def __init__(self, gameState, name, metrics):
        Group.__init__(self)			#initialize base class
        self.gameState = gameState
        self.name = name
        self.metrics = {}	        #:dictionary of environment metrics, keyed by metric name
        for metric in metrics:
            self.metrics[metric.name] = metric
            metric.diffuse() #diffuse once during initialization
            
    def initBirds(self):
        """Place random birds throughout the map"""
        for i in range(20):
            self.add(Bird(self.gameState, self.gameState.randomPosition()))

    def initHawks(self):
        """Place random hawks throughout the map"""
        for i in range(10):
            self.add(Hawk(self.gameState, self.gameState.randomPosition()))
            
    def update(self):
        """Updates member entities then applies diffusion to metric arrays"""
        Group.update(self) #the base update method calls update on all sprites in the group
        
        for entity in self.sprites():
            entity.eat()
        # lazy way of doing this - should we have separate group classes?
        if self.name == "food":
            if random() < .1:
                self.add(Food(self.gameState, self.gameState.randomPosition()))
            #clear the array and set all food cells to 1
            self.metrics["food"].clear()
            for entity in self.sprites():
                self.metrics["food"].array[entity.discretePosition] = 1
            #diffuse the food array
            self.metrics["food"].diffuse()
        elif self.name == "bird":
            self.metrics["attract"].clear()
            for entity in self.sprites():
                self.metrics["attract"].array[entity.discretePosition] = 1
            #diffuse the food array
            self.metrics["attract"].diffuse()

        #Diffuse metric arrays
#        for metric in self.metrics.itervalues():
#            metric.diffuse()
                
    def getMetricNames(self):
        """Returns a list of names for metrics maintained by this group"""
        return self.metrics.keys()

    def getRankedDirections(self, position):
        """Find the direction with the maximum diffusion value for the given metric"""
        if self.name == "bird":
            metric = self.gameState.entityGroups["food"].metrics["food"]
        elif self.name == "hawk":
            metric = self.gameState.entityGroups["bird"].metrics["attract"]
            
        return metric.getRankedDirections(position)

