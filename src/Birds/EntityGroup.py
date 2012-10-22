from pygame.sprite import Group
from GameState import Metric

class EntityGroup(Group):
	"""This class manages a group of entities and their diffused environment metrics"""

	groupName = None		#:A name for this group
	gameState = None		#:A reference to the master gameState object
        updatedEntities = None          #:A group that will contain updated entities
	metrics = {}		        #:dictionary of environment metrics, keyed by metric name

	def __init__(self, gameState, groupName, metrics):
		Group.__init__(self)			#initialize base class
		self.gameState = gameState
		self.groupName = groupName
		self.updatedEntities = Group()
                for metric in metrics:
                        self.metrics[metric.name] = metric
                        metric.diffuse() #diffuse once during initialization

	def update(self):
		"""Updates member entities then applies diffusion to metric arrays"""
		Group(self).update() #call the update method for the base Group class
		#Diffuse metric arrays
                for metric in self.metrics:
                    metric.diffuse()

	def getUpdatedEntities(self):
		pass # TODO

	def addEntity(self, entity):
		Group(self).add(entity) #call the base class add method

	def removeEntity(self, entity):
		"""Remove the given entity from this group"""
		Group(self).remove(entity) #call the base class remove method

	def getMetricNames(self):
		"""Returns a list of names for metrics maintained by this group"""
		return self.metrics.keys()
