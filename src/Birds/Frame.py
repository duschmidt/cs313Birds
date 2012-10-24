from Metric import Metric
import pygame, time
from pygame.locals import *

BACKGROUND_COLOR = (100, 100, 100)
OBSTACLE_COLOR = (0, 0, 0)
EMPTY_COLOR = (255, 255, 255)

class Cell:
    #width/height of an individual cell
    width = height = 0
    #discrete pos
    col = row = 0
    #pos in pixels (upper left)
    x = y = 0
    #default color is white
    color = EMPTY_COLOR
    
    def __init__(self, col, row, obstacle):
        if obstacle:
            self.color = OBSTACLE_COLOR
        self.col = col
        self.row = row
        self.x = col * self.width
        self.y = (row + 1) * self.height
        
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
class Frame:
    running = False
    # width and height in pixels
    width = height = 0
    # reference to GameState (NOTE: Not sure if we want/need this dependency.  the Main.py controller can get info from GameState and send it to Frame)
    gameState = None
    
    def __init__(self, pixelDims, discreteDims):
        self.width, self.height = pixelDims
        self.numCols, self.numRows = discreteDims
        Cell.width  = self.width / float(self.numCols)
        Cell.height = self.height / float(self.numRows)
        
        self.grid = []
        for col in range(self.numCols):
            self.grid.append([])
            for row in range(self.numRows):
                self.grid[col].append(Cell(col, row, not Metric.obstacleAry[col, row]))

        # init pygame-specific stuff
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.running = True
        
    def positionToDiscrete(self, position):
        """Convert a continuous position given by position into discrete cells"""
        x,y = position
        return ((int)(self.numCols * x / self.width), (int)(self.numRows * y / self.height))

    def drawEnvironment(self):
        # Blit the background
        self.screen.blit(self.background, (0,0))
        # fill BG
        self.background.fill(BACKGROUND_COLOR)

        # Draw all cells
        for col in range(self.numCols):
            for row in range(self.numRows):
                self.grid[col][row].draw(self.screen)
        
    def draw(self):
        """Draw one frame"""
        # Get our event. Prosessing one at a time because of the nature of our game,
        # we don't need to consider the possibility of simultanious input.
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == KEYDOWN:
            if event.key == 13 :
                pass
        elif event.type == MOUSEBUTTONDOWN:
            col,row = self.positionToDiscrete(event.pos)
            # TODO : do something with click at col, row

        self.drawEnvironment()
        pygame.display.update()
            
