from MovingEntity import MovingEntity

class Hawk(MovingEntity):
    """This is the entity class for birds"""
    name = "hawk"
    imageName = "hawk.png"
    
    def update(self):
        """Update the bird's position"""
        MovingEntity.update(self) # parent class update

    def eat(self):
        # birds eat food
        for entity in self.gameState.getEntitiesAtPosition(self.discretePosition):
            if entity.name == "bird":
                self.gameState.removeEntity(entity)
