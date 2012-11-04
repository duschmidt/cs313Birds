from GameState import GameState
from Frame import Frame

if __name__ == '__main__' :
    gameState = GameState("../../data/map4.map")
    frame = Frame((780, 780), gameState.getDiscreteDimensions())
    gameState.initBirds()
    gameState.initHawks()
    
    while frame.running:
        gameState.update()
        frame.draw(gameState, gameState.getGroups())
    