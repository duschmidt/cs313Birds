from pygame.sprite import Group

class EntityGroup(Group):

	gameState = None
	entityGroup = None
	updatedEntities = None
	diffusionRate = 0.0

	def __init__(self, gameState, diffRate):
		self.gameState = gameState
		self.entityGroup = Group()
		self.updatedEntities = Group()

	def update(self):
		pass

	def getUpdatedEntities():
		return Group()

	def addEntity(entity):
		pass

	def removeEntity(entity):
		pass

