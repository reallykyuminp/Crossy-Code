from cmu_graphics import *
from PIL import Image
import math, copy
import random
import time

class sprite():
    def __init__(self, x, y, width, height, imagefile):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        #creating two dimensional images
        self.twoDImage = create2DImage(self.width, self.height, imagefile)

    def is_collision(self, other):
        return ((abs((self.x - other.x + 25)*2) < (self.width + other.width)) and 
                (abs((self.y - other.y + 25)*2) < (self.height + other.height)))

class player(sprite):
    def __init__(self, x, y, width, height, imagefile):
        sprite.__init__(self, x, y, width, height, imagefile)
        self.dx = 0
        self.row = 8

    def up(self):
        (xChange, yChange) = twoDimensionToIsometric(0, -50)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)
        if self.row < 8:
            self.row += 1
    
    def down(self):
        (xChange, yChange) = twoDimensionToIsometric(0, 50)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)
        self.row -= 1
    
    def left(self):
        (xChange, yChange) = twoDimensionToIsometric(-50, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)
    
    def right(self):
        (xChange, yChange) = twoDimensionToIsometric(50, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)

    def move(self):
        (xChange, yChange) = twoDimensionToIsometric(self.dx, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)

class tree(sprite):
    def __init__(self, x, y, width, height, imagefile):
        sprite.__init__(self, x, y, width, height, imagefile)
        self.dx = 0

    def move(self):
        (xChange, yChange) = twoDimensionToIsometric(self.dx, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)

class car(sprite):
    def __init__(self, x, y, width, height, imagefile, dx):
        sprite.__init__(self, x, y, width, height, imagefile)
        self.dx = dx
    #creating isometric images by rotating and resizing
        isoImage = Image.open(imagefile).convert('RGBA')
        isoImage = isoImage.rotate(-25)
        isoImage = isoImage.resize((self.width, self.height))
        isoImage = CMUImage(isoImage)
        self.isoImage = isoImage
    #moves across the row
    def move(self):
        (xChange, yChange) = twoDimensionToIsometric(self.dx, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)
    #car returns on the other side when it leaves the screen
        if self.dx > 0 and self.y >= 600:
            self.x = findBorderX(self.x, self.y, self.dx)
            self.y = 0
        if self.dx < 0 and self.y <= 0:
            self.x = findBorderX(self.x, self.y, self.dx)
            self.y = 600

class log(sprite):
    def __init__(self, x, y, width, height, imagefile, dx):
        sprite.__init__(self, x, y, width, height, imagefile)
        self.dx = dx
    #creating isometric images by rotating and resizing
        self.isoImage = createIsoImage(self.width, self.height, imagefile)
    #moves across the row
    def move(self):
        (xChange, yChange) = twoDimensionToIsometric(self.dx, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)
    #car returns on the other side when it leaves the screen
        if self.dx > 0 and self.y >= 600:
            self.x = findBorderX(self.x, self.y, self.dx)
            self.y = 0
        if self.dx < 0 and self.y <= 0:
            self.x = findBorderX(self.x, self.y, self.dx)
            self.y = 600

class racecar(sprite):
    def __init__(self, x, y, width, height, imagefile, dx):
        sprite.__init__(self, x, y, width, height, imagefile)
        self.dx = dx
        self.movingTime = random.randint(6,10)
        self.currTime = time.time()
    #creating isometric images by rotating and resizing
        isoImage = Image.open(imagefile).convert('RGBA')
        isoImage = isoImage.rotate(-25)
        isoImage = isoImage.resize((self.width, self.height))
        isoImage = CMUImage(isoImage)
        self.isoImage = isoImage
    #moves across the row
    def move(self):
        (xChange, yChange) = twoDimensionToIsometric(self.dx, 0)
        (self.x, self.y) = (self.x + xChange, self.y + yChange)

#converts 2D coordinates to isometric coordinates
def twoDimensionToIsometric(twoDX, twoDY):
    return (twoDX-twoDY, (twoDX+twoDY)/2)

#converts isometric coordinates to 2D coordinates
def isometricToTwoDimension(isoX, isoY):
    twoDX = (isoX + isoY * 2)/2
    return (twoDX, (-1 * isoX) + twoDX)

#calculates the x coordinate when an obstacles moves off the screen
def findBorderX(currX, currY, dx):
    if dx > 0:
        (xChange, yChange) = twoDimensionToIsometric(-dx, 0)
        while currY >= 0:
            (currX, currY) = (currX + xChange, currY + yChange)
        return currX
    else:
        (xChange, yChange) = twoDimensionToIsometric(-dx, 0)
        while currY <= 600:
            (currX, currY) = (currX + xChange, currY + yChange)
        return currX

#creating two dimensional images
def create2DImage(width, height, imagefile):
    twoDImage = Image.open(imagefile).convert('RGBA')
    twoDImage = twoDImage.resize((width, height))
    twoDImage = CMUImage(twoDImage)
    return twoDImage

#creating isometric images
def createIsoImage(width, height, imagefile):
    isoImage = Image.open(imagefile).convert('RGBA')
    isoImage = isoImage.rotate(45, expand=1)
    isoImage = isoImage.resize((width, height))
    isoImage = CMUImage(isoImage)
    return isoImage

def onAppStart(app):
    app.width = 1000
    app.height = 600
    app.rows = 25
    app.cols = 22
    app.gameMode = 'single'
    app.gamePaused = False
    app.tileSize = app.width // 20
    app.board = []
    app.obstacleBoard = []
    app.sprites = []
    app.terrainTypes = ['grass', 'river', 'road']
    app.logSpeeds = ['fast', 'medium', 'slow']
    app.carSpeeds = ['fast', 'medium', 'slow']
    app.stepsPerSecond = 180
    restartSinglePlayer(app)

def restartSinglePlayer(app):
    app.gameOver = False
    genTerrainList(app)
    genObstaclesProperties(app)
    genObstacles(app)

    # set player1 start position
    app.player1 = player(325, 412,
                         app.tileSize, app.tileSize, 
                         'Player1Forward.png')
    app.sprites.append([app.player1])
    
def genTerrainList(app):
    #create a list with order of terrain (first 8 rows are always grass)
    app.terrainList = ['grass', 'grass', 'grass', 'grass', 'grass', 'grass',
                       'grass', 'grass', 'grass', 'grass']
    #follow rows are produced randomly depending on percentage
    for row in range(app.rows-10):
        terrainIdx = randrange(100)
    #percentages for terrain generation
    #(grass=30%, river=30%, road=40%)
        if terrainIdx <= 30:
            terrainIdx = 0
        elif terrainIdx <= 60:
            terrainIdx = 1
        else:
            terrainIdx = 2
        app.terrainList.append(app.terrainTypes[terrainIdx])
    
def genObstaclesProperties(app):
    #generating obstacles
    for terrainIdx in range(len(app.terrainList)):
        if app.terrainList[terrainIdx] == 'grass':
            #randomized num of trees generated
            numOfTrees = choice([2,3,4,5])
            app.board.append(numOfTrees)
        elif app.terrainList[terrainIdx] == 'river':
            #randomized log length, speed, and direction
            logLength = choice([2,3,4])
            logSpeed = choice([10,20,30])
            logDirection = choice([-1,1])
            app.board.append((logLength, logSpeed, logDirection))
        elif app.terrainList[terrainIdx] == 'road':
            #randomized car speed, direction, and color
            carSpeed = choice([10,20,30])
            carDirection = choice([-1,1])
            if carDirection == 1:
                carColor = choice(['GreenCar.png', 'BlueCar.png', 
                                   'OrangeCar.png'])
            else:
                carColor = choice(['GreenCarReversed.png', 
                                   'BlueCarReversed.png', 
                                   'OrangeCarReversed.png'])
            app.board.append((carSpeed, carDirection, carColor))

def genObstacles(app):
    startXTerrain = app.width - app.tileSize//2
    startYTerrain = app.tileSize * (-1/8)
    rightRowCount = -1
    leftRowCount = app.rows - 3
    for obstacleIdx in reversed(range(len(app.board))):
        yTerrain = startYTerrain
        xTerrain = startXTerrain
        rowList = []
        if obstacleIdx <= 15:
            rightRowCount += 1
        if obstacleIdx >= 7:
            leftRowCount -= 1
        if app.terrainList[obstacleIdx] == 'grass':
            #generating trees
            numOfTrees = app.board[obstacleIdx]
            treeSet = chooseTrees(numOfTrees)
            for col in range(app.cols):
                if (col <= rightRowCount):
                    currTree = tree(xTerrain, yTerrain, app.tileSize, app.tileSize, 'Tree.png')
                    rowList.append(currTree)
                elif (col >= app.rows - leftRowCount) and (obstacleIdx >= 7):
                    currTree = tree(xTerrain, yTerrain, app.tileSize, app.tileSize, 'Tree.png')
                    rowList.append(currTree)
                else:
                    if col in treeSet:
                        currTree = tree(xTerrain, yTerrain, app.tileSize, app.tileSize, 'Tree.png')
                        rowList.append(currTree)
                #shift for each col tile
                (xChange, yChange) = twoDimensionToIsometric(app.tileSize, 0)
                xTerrain -= xChange
                yTerrain -= yChange

        elif app.terrainList[obstacleIdx] == 'river':
            #generating logs
            logLength, logSpeed, logDirection = app.board[obstacleIdx]
            for col in range(app.cols):
                if logLength == 2:
                    logSet = {1,2,6,7,11,12,16,17}
                    if col in logSet:
                        currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                        rowList.append(currLog)
                elif logLength == 3:
                    logSet = {1,2,3,7,8,9,13,14,15,19,20}
                    if col in logSet:
                        currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                        rowList.append(currLog)
                elif logLength == 4:
                    logSet = {1,2,3,4,8,9,10,11,15,16,17,18}
                    if col in logSet:
                        currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                        rowList.append(currLog)
                #shift for each col tile
                (xChange, yChange) = twoDimensionToIsometric(app.tileSize, 0)
                xTerrain -= xChange
                yTerrain -= yChange

        elif app.terrainList[obstacleIdx] == 'road':
            #generating cars
            carSpeed, carDirection, carColor = app.board[obstacleIdx]
            for col in range(app.cols):
                carSet = {1, 5, 9, 13, 17, 20}
                if col in carSet:
                    currCar = car(xTerrain, yTerrain, app.tileSize, app.tileSize, carColor, carSpeed * carDirection)
                    rowList.append(currCar)

        #shift for each row tile
        app.obstacleBoard.append(rowList)
        app.sprites.append(rowList)
        startYTerrain += app.tileSize

def chooseTrees(numOfTrees):
    treeSet = set()
    while numOfTrees > 0:
        randSpot = randrange(0, 15)
        if randSpot not in treeSet:
            treeSet.add(randSpot)
            numOfTrees -= 1
    return treeSet

def redrawAll(app):
    genTerrain(app)
    drawObstacles(app)
    drawImage(app.player1.twoDImage, app.player1.x, app.player1.y)

def genTerrain(app):
    #terrain generation
    startXTerrain = app.width - app.tileSize
    startYTerrain = 0
    for terrain in reversed(app.terrainList):
        yTerrain = startYTerrain
        xTerrain = startXTerrain
        for col in range(app.cols):
            if terrain == 'grass':
                terrainBlock = createIsoImage(2 * app.tileSize, app.tileSize, 'GrassBlock.png')
            elif terrain == 'river':
                terrainBlock = createIsoImage(2 * app.tileSize, app.tileSize, 'WaterBlock.png')
            else:
                terrainBlock = createIsoImage(2 * app.tileSize, app.tileSize, 'RoadBlock.png')
            drawImage(terrainBlock, xTerrain, yTerrain)
            #shift for each col tile
            (xChange, yChange) = twoDimensionToIsometric(app.tileSize, 0)
            xTerrain -= xChange
            yTerrain -= yChange
        #shift for each row tile
        startYTerrain += app.tileSize

def drawObstacles(app):
    for rowList in app.obstacleBoard:
        for obstacle in rowList:
            if isinstance(obstacle, tree):
                drawImage(obstacle.twoDImage, obstacle.x, obstacle.y) 
            elif isinstance(obstacle, log):
                drawImage(obstacle.isoImage, obstacle.x, obstacle.y + (1/4) * app.tileSize)
            elif isinstance(obstacle, car):
                drawImage(obstacle.isoImage, obstacle.x, obstacle.y + (1/4) * app.tileSize)       

def onKeyPress(app, key):
    if key == 'up' or key == 'space':
        app.player1.twoDImage = create2DImage(app.player1.width, app.player1.height, 'Player1Forward.png')
        if app.player1.row < 8:
            app.player1.up()
        else:
            app.player1.up()
            shiftBoard(app)
    elif key == 'down':
        app.player1.twoDImage = create2DImage(app.player1.width, app.player1.height, 'Player1Back.png')
        app.player1.down()
    elif key == 'left':
        app.player1.twoDImage = create2DImage(app.player1.width, app.player1.height, 'Player1Left.png')
        app.player1.left()
    elif key == 'right':
        app.player1.twoDImage = create2DImage(app.player1.width, app.player1.height, 'Player1Right.png')
        app.player1.right()
    
def shiftBoard(app):
    terrainIdx = randrange(100)
    #percentages for terrain generation
    #(grass=30%, river=20%, road=40%, highway=10%)
    if terrainIdx <= 30:
        terrainIdx = 0
    elif terrainIdx <= 60:
        terrainIdx = 1
    else:
        terrainIdx = 2
    #shift the terrains downward
    app.terrainList.append(app.terrainTypes[terrainIdx])
    app.terrainList.pop(0)

    #create new obstacle properties
    if app.terrainTypes[terrainIdx] == 'grass':
        numOfTrees = choice([2,3,4,5])
        app.board.append(numOfTrees)
    elif app.terrainTypes[terrainIdx] == 'river':
        #randomized log length, speed, and direction
        logLength = choice([2,3,4])
        logSpeed = choice([10,20,30])
        logDirection = choice([-1,1])
        app.board.append((logLength, logSpeed, logDirection))
    elif app.terrainTypes[terrainIdx] == 'road':
        #randomized car speed, direction, and color
        carSpeed = choice([10,20,30])
        carDirection = choice([-1,1])
        if carDirection == 1:
            carColor = choice(['GreenCar.png', 'BlueCar.png', 
                               'OrangeCar.png'])
        else:
            carColor = choice(['GreenCarReversed.png', 
                               'BlueCarReversed.png', 
                               'OrangeCarReversed.png'])
        app.board.append((carSpeed, carDirection, carColor))
    app.board.pop(0)
    
    #shift old obstacles downward
    for row in app.sprites:
        for sprite in row:
            (xChange, yChange) = twoDimensionToIsometric(0, 50)
            (sprite.x, sprite.y) = (sprite.x + xChange, sprite.y + yChange)

    #create new obstacles
    xTerrain = app.width - app.tileSize//2
    yTerrain = app.tileSize * (-1/8)
    leftRowCount = app.rows - 4
    rowList = []
    if app.terrainList[-1] == 'grass':
        #generating trees
        numOfTrees = app.board[-1]
        treeSet = chooseTrees(numOfTrees)
        for col in range(app.cols):
            if (col >= app.rows - leftRowCount):
                currTree = tree(xTerrain, yTerrain, app.tileSize, app.tileSize, 'Tree.png')
                rowList.append(currTree)
            else:
                if col in treeSet:
                    currTree = tree(xTerrain, yTerrain, app.tileSize, app.tileSize, 'Tree.png')
                    rowList.append(currTree)
            #shift for each col tile
            (xChange, yChange) = twoDimensionToIsometric(app.tileSize, 0)
            xTerrain -= xChange
            yTerrain -= yChange

    elif app.terrainList[-1] == 'river':
        #generating logs
        logLength, logSpeed, logDirection = app.board[-1]
        for col in range(app.cols):
            if logLength == 2:
                logSet = {1,2,6,7,11,12,16,17}
                if col in logSet:
                    currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                    rowList.append(currLog)
            elif logLength == 3:
                logSet = {1,2,3,7,8,9,13,14,15,19,20}
                if col in logSet:
                    currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                    rowList.append(currLog)
            elif logLength == 4:
                logSet = {1,2,3,4,8,9,10,11,15,16,17,18}
                if col in logSet:
                    currLog = log(xTerrain, yTerrain, 2 * app.tileSize, app.tileSize, 'Log.png', logSpeed * logDirection)
                    rowList.append(currLog)
            #shift for each col tile
            (xChange, yChange) = twoDimensionToIsometric(app.tileSize, 0)
            xTerrain -= xChange
            yTerrain -= yChange

    elif app.terrainList[-1] == 'road':
        #generating cars
        carSpeed, carDirection, carColor = app.board[-1]
        for col in range(app.cols):
            carSet = {1, 5, 9, 13, 17, 20}
            if col in carSet:
                currCar = car(xTerrain, yTerrain, app.tileSize, app.tileSize, carColor, carSpeed * carDirection)
                rowList.append(currCar)

    app.obstacleBoard.append(rowList)
    app.obstacleBoard.pop(0)
    app.sprites.append(rowList)
    app.sprites.pop(0)

def onStep(app):
    #move all obstacles accordingly
    for row in app.sprites:
        for sprite in row:
            sprite.move()
    #player.dx is set to 0 when it is no longer on the log
    app.player1.dx = 0
    #check for any collisions with player
    for row in app.sprites:
        for sprite in row:
            if app.player1.is_collision(sprite):
                if isinstance(sprite, car) and app.terrainList[app.player1.row] == 'road':
                    restartSinglePlayer(app)
                    break
                elif isinstance(sprite, log) and app.terrainList[app.player1.row] == 'river':
                    app.player1.dx = sprite.dx
                    break
            if app.terrainList[app.player1.row] == 'river':
                restartSinglePlayer(app)
                    

    #gameover when player leaves the screen
    if app.player1.y >= 600 or app.player1.y <= 0:
        restartSinglePlayer(app)

def main():
    runApp()
main()