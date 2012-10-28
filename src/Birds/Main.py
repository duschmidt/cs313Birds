from GameState import GameState
from Frame import Frame

if __name__ == '__main__' :
    gameState = GameState("../../data/map1.map")
    frame = Frame((600, 600), gameState.getDimensions())
    while frame.running:
        gameState.update()
        frame.draw(gameState.getGroups())
    