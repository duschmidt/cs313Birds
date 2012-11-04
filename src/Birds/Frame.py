from Metric import Metric
import pygame, time
from pygame.locals import *
import numpy as np

BACKGROUND_COLOR = (100, 100, 100)
OBSTACLE_COLOR = (0, 0, 0)
EMPTY_COLOR = (200, 200, 200)

class Cell:
    #width/height of an individual cell
    width = height = 0
    #discrete pos
    col = row = 0
    #default color is white
    color = EMPTY_COLOR
    
    def __init__(self, col, row, obstacle):
        if obstacle:
            self.color = OBSTACLE_COLOR
        self.col = col
        self.row = row
        self.rect = (col * self.width, row * self.height, self.width, self.height)
        
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

    def draw(self, screen):
        screen.fill(self.color, rect=self.rect)

def calcColor(value):
    val = int((value * 200))

    return (200, 200 - val, 200 - val)
    
class Frame:
    running = False
    # width and height in pixels
    width = height = 0
    
    def __init__(self, pixelDims, discreteDims):
        self.width, self.height = pixelDims
        self.numCols, self.numRows = discreteDims
        Cell.width  = self.width / self.numCols
        Cell.height = self.height / self.numRows
        
        self.grid = []
        for col in range(self.numCols):
            self.grid.append([])
            for row in range(self.numRows):
                self.grid[col].append(Cell(col, row, not Metric.obstacleAry[col, row]))
                

        # init pygame-specific stuff
        pygame.init()
        # ignore mousemotions and activeevents (which happen when focus changes)
        pygame.event.set_blocked([MOUSEMOTION, ACTIVEEVENT])
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.running = True
        
    def drawEnvironment(self, spriteGroups):
        # Blit the background
        self.screen.blit(self.background, (0,0))
        # fill BG
        self.background.fill(BACKGROUND_COLOR)

        # Draw all cells
        for col in range(self.numCols):
            for row in range(self.numRows):
                self.grid[col][row].draw(self.screen)
                
    def handleEvents(self, gameState):
        """Check all allowed events that have occured in the last frame and handle events of interest"""
        while True:
            event = pygame.event.poll()
            if event.type == NOEVENT:
                # reached the end of the event queue. break
                break
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == 13:
                    pass
            elif event.type == MOUSEBUTTONUP:
                col,row = gameState.positionToDiscrete(event.pos)
                # add food at click position
                gameState.addFood((col, row))

    def draw(self, gameState, entityGroups):
        """Draw one frame"""
        # Get our event. Prosessing one at a time because of the nature of our game,
        # we don't need to consider the possibility of simultanious input.
        self.handleEvents(gameState)
        self.drawEnvironment(entityGroups)
        for entityGroup in entityGroups:
            entityGroup.draw(self.screen)
            
        pygame.display.update()
            


