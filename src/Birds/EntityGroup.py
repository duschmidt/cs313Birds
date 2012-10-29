from pygame.sprite import Group

from Metric import Metric
from Food import Food
from Bird import Bird

class EntityGroup(Group):
    """This class manages a group of entities and their diffused environment metrics"""

    gameState = None            #:Reference to global game state
    groupName = None		#:A name for this group
    metrics = {}	        #:dictionary of environment metrics, keyed by metric name

    def __init__(self, gameState, groupName, metrics):
        Group.__init__(self)			#initialize base class
        self.gameState = gameState
        self.groupName = groupName
        for metric in metrics:
            self.metrics[metric.name] = metric
            metric.diffuse() #diffuse once during initialization
            
    def initBirds(self):
        """Place random birds throughout the map"""
        for i in range(8):
            self.add(Bird(self.gameState, 1, self.gameState.randomPosition()))
            
    def update(self):
        """Updates member entities then applies diffusion to metric arrays"""
        Group.update(self) #the base update method calls update on all sprites in the group
        
        if self.groupName == "Food": # lazy way of doing this - should we have separate group classes?
            self.add(Food(self.gameState, 0, self.gameState.randomPosition()))

        #clear the array and set all food cells to 1
        if self.groupName == "Food":
            self.metrics["attract"].clear()
            for entity in self.sprites():
                self.metrics["attract"].array[self.gameState.positionToDiscrete(entity.position)] = 1
                                   
        #Diffuse metric arrays
        for metric in self.metrics.itervalues():
            metric.diffuse()

    def getMetricNames(self):
        """Returns a list of names for metrics maintained by this group"""
        return self.metrics.keys()

    def neighborhood(self, position):
        return self.metrics["attract"].array[position]