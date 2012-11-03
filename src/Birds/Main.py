from GameState import GameState
from Frame import Frame

if __name__ == '__main__' :
    gameState = GameState("../../data/map4.map")
    frame = Frame((600, 600), gameState.getDiscreteDimensions())
    gameState.initBirds()
    
    while frame.running:
        gameState.update()
        frame.draw(gameState, gameState.getGroups())
    