from pygame.sprite import Group

class EntityGroup(Group):
	"""This class manages a group of entities and their diffused environment metrics"""

	groupName = None		#:A name for this group
	gameState = None		#:A reference to the master gameState object
	updatedEntities = None	#:A group that will contain updated entities
	diffusionRates = {}		#:dictionary of diffusion rates keyed by metric name
	metricArrays = {}		#:dictionary of environment metric arrays keyed by metric name

	def __init__(self, gameState, diffRate, groupName):
		Group.__init__(self)			#initialize base class
		self.gameState = gameState
		self.diffusionRate = diffRate
		self.groupName = groupName
		self.updatedEntities = Group()

	def update(self):
		"""Updates member entities then applies diffusion to metric arrays"""
		Group(self).update() #call the update method for the base Group class

		#TODO Diffuse metric arrays
		pass

	def getUpdatedEntities(self):
		pass

	def addEntity(self, entity):
		Group(self).add(entity)#call the base class add method
		pass

	def removeEntity(self, entity):
		"""Remove the given entity from this group"""
		Group(self).remove(entity) #call the base class remove method
		pass

	def getMetricNames(self):
		"""Returns a list of names for metrics maintained by this group"""
		pass

