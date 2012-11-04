from MovingEntity import MovingEntity

class Bird(MovingEntity):
    """This is the entity class for birds"""
    name = "bird"
    imageName = "bird.png"
    
    def update(self):
        """Update the bird's position"""
        MovingEntity.update(self) # parent class update

    def eat(self):
        # birds eat food
        for entity in self.gameState.getEntitiesAtPosition(self.discretePosition):
            if entity.name == "food":
                self.gameState.removeEntity(entity)
        