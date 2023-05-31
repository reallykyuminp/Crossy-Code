from cmu_graphics import *
from PIL import Image
import math, copy
import random
import time

# --------------------- sources ---------------------------- #
#character sprites: https://opengameart.org/content/character-rpg-sprites
#log and tree sprites: https://opengameart.org/content/medieval-rts-120
#car sprites: https://opengameart.org/content/isometric-vehicles-3
#read file and write file: https://realpython.com/read-write-files-python/

#read file 
def readFile(path):
    with open(path, 'rt') as f:
        return ''.join(f.readlines())
    
#write file
def writeFile(path, contents):
    with open(path, 'wt') as f:
        f.write(contents)

#creating isometric images
def createIsoImage(width, height, imagefile):
    isoImage = Image.open(imagefile).convert('RGBA')
    isoImage = isoImage.rotate(45, expand=1)
    isoImage = isoImage.resize((width, height))
    isoImage = CMUImage(isoImage)
    return isoImage

#given a row, col returns an x, y using 2D to isometric conversion
def getCoord(app, row, col):
    startX = -1 * app.tileSize * 12.5
    startY =  app.height / 2 - app.tileSize * .4
    x = startX + col * app.tileSize + row * app.tileSize
    y = startY- row * app.tileSize//2 + col * app.tileSize//2
    return x, y

class sprite():
    def __init__(self, row, col, width, height, imagefile):
        self.row, self.col = row, col
        self.width = width
        self.height = height
        #creating two dimensional images
        self.image = self.create2DImage(self.width, self.height, imagefile)    

    def create2DImage(self, width, height, imagefile):
        twoDImage = Image.open(imagefile).convert('RGBA')
        twoDImage = twoDImage.resize((width, height))
        twoDImage = CMUImage(twoDImage)
        return twoDImage
    
    def is_collision(self, other):
        return self.row == other.row and self.col == other.col

class player(sprite):
    def __init__(self, row, col):
        sprite.__init__(self, row, col, 50, 50, 'Player1Forward.png')

    def up(self):
        if self.row < 9: self.row += 1
        self.image = self.create2DImage(self.width, self.height, 
                                        'Player1Forward.png')

    def down(self):
        if self.row > 3: self.row -= 1
        self.image = self.create2DImage(self.width, self.height, 
                                        'Player1Back.png')

    def right(self):
        self.col = (self.col + 1) % 22
        self.image = self.create2DImage(self.width, self.height, 
                                        'Player1Right.png')

    def left(self):
        self.col = (self.col - 1) % 22
        self.image = self.create2DImage(self.width, self.height, 
                                        'Player1Left.png')
        
class tree(sprite):
    def __init__(self, row, col):
        sprite.__init__(self, row, col, 50, 50, 'Tree.png')

    def down(self):
        self.row -= 1

class log(sprite):
    def __init__(self, row, col, speed, direction):
        sprite.__init__(self, row, col, 50, 50, 'Log.png')
        self.image = createIsoImage(2 * self.width, self.height, 'Log.png')
        self.speed = speed
        self.direction = direction 

    def down(self):
        self.row -= 1   

    def right(self):
        self.col = (1 + self.col) % 22

    def left(self):
        self.col = (self.col - 1) % 22

class car(sprite):
    def __init__(self, row, col, speed, direction, imagefile):
        sprite.__init__(self, row, col, 50, 50, imagefile)
        isoImage = Image.open(imagefile).convert('RGBA')
        isoImage = isoImage.rotate(-25)
        isoImage = isoImage.resize((self.width, self.height))
        isoImage = CMUImage(isoImage)
        self.image = isoImage
        self.speed = speed
        self.direction = direction

    def down(self):
        self.row -= 1   

    def right(self):
        self.col = (1 + self.col) % 22

    def left(self):
        self.col = (self.col - 1) % 22

def onAppStart(app):
    app.width = 1000
    app.height = 600
    app.rows = 25
    app.cols = 22
    app.tileSize = app.width//20
    app.terrainTypes = ['grass', 'river', 'road']
    app.stepsPerSecond = 5
    app.matrix = makeList(app.rows, app.cols)
    app.user = ''
    restart(app)
    app.startingScreen = True
    app.userScreen = False

def restart(app):
    app.gameOver = False
    app.gamePaused = False
    app.score = 0
    app.store = False
    app.stepCount = 0
    genTerrainList(app)
    for row in range(app.rows):
        app.matrix[row] = [app.terrainList[row]] * app.cols
    app.treesList = []
    genTreesList(app)
    app.logsList = []
    genLogsList(app)
    app.carsList = []
    genCarsList(app)
    app.player = player(4, 11)
    app.leadtxt = readFile('lead.txt')
    
def genTerrainList(app):
    #create a list with order of terrain (first 10 rows are always grass)
    app.terrainList = ['grass', 'grass', 'grass', 'grass', 'grass', 
                       'grass', 'grass', 'grass', 'grass', 'grass']
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

#generate starting list containing all tree images
def genTreesList(app):
    for row in range(app.rows):
        numOfTrees = choice([2,3,4])
        if app.matrix[row][0] == 'grass':
            for col in range(app.cols):
                if col <= 5 or col >= 16:
                    app.treesList.append(tree(row, col))
            for num in range(numOfTrees):
                randCol = randrange(6, 16)
                if row != 4 and randCol != 11:
                    app.treesList.append(tree(row, randCol))

#generate starting list containing all log images
def genLogsList(app):
    for row in range(app.rows):
        #randomized log length, speed, and direction
        logLength = choice([2,3,4])
        logSpeed = choice([100,200,400])
        logDirection = choice(['left', 'right'])
        if app.matrix[row][0] == 'river':
            for col in range(app.cols):
                if logLength == 2:
                    logSet = {1,2,6,7,11,12,16,17,19,20}
                    if col in logSet:
                        app.logsList.append(log(row, col, logSpeed, logDirection))
                elif logLength == 3:
                    logSet = {1,2,3,7,8,9,13,14,15,18,19}
                    if col in logSet:
                        app.logsList.append(log(row, col, logSpeed, logDirection))
                elif logLength == 4:
                    logSet = {1,2,3,4,8,9,10,11,15,16,17,18}
                    if col in logSet:
                        app.logsList.append(log(row, col, logSpeed, logDirection))

#generate starting list containing all car images
def genCarsList(app):
    for row in range(app.rows):
        carSpeed = choice([100,200,400])
        carDirection = choice(['left','right'])
        if carDirection == 'right':
            carColor = choice(['GreenCar.png', 'BlueCar.png', 
                                'OrangeCar.png'])
        else:
            carColor = choice(['GreenCarReversed.png', 
                                'BlueCarReversed.png', 
                                'OrangeCarReversed.png'])
        if app.matrix[row][0] == 'road':
            numOfCars = randrange(3,4,5)
            for num in range(numOfCars):
                randCol = randrange(app.cols)
                app.carsList.append(car(row, randCol, carSpeed,carDirection, carColor))

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
    for row in range(app.rows):
        app.matrix[row] = [app.terrainList[row]] * app.cols

def shift(app):
    #shift each tree down a row
    for trees in app.treesList:
        if trees.row == 0:
            app.treesList.remove(trees)
        else:
            trees.row -= 1
    numOfTrees = choice([2,3,4])
    #create new row of trees
    if app.matrix[24][0] == 'grass':
        for col in range(app.cols):
            if col <= 5 or col >= 16:
                app.treesList.append(tree(24, col))
        for num in range(numOfTrees):
            randCol = randrange(6, 16)
            app.treesList.append(tree(24, randCol))

    #shift each log down a row
    for logs in app.logsList:
        if logs.row == 0:
            app.logsList.remove(logs)
        else:
            logs.row -= 1
    #create new row of logs
    logLength = choice([2,3,4])
    logSpeed = choice([100, 200, 400])
    logDirection = choice(['left', 'right'])
    if app.matrix[24][0] == 'river':
        for col in range(app.cols):
            if logLength == 2:
                logSet = {1,2,6,7,11,12,16,17,19,20}
                if col in logSet:
                    app.logsList.append(log(24, col, logSpeed, logDirection))
            elif logLength == 3:
                logSet = {1,2,3,7,8,9,13,14,15,18,19}
                if col in logSet:
                    app.logsList.append(log(24, col, logSpeed, logDirection))
            elif logLength == 4:
                logSet = {1,2,3,4,8,9,10,11,15,16,17,18}
                if col in logSet:
                    app.logsList.append(log(24, col, logSpeed, logDirection))
    
    #shift each row of cars down 
    for cars in app.carsList:
        if cars.row == 0:
            app.carsList.remove(cars)
        else:
            cars.row -= 1
    #create new row of cars
    carSpeed = choice([100,200,400])
    carDirection = choice(['left','right'])
    if carDirection == 'right':
        carColor = choice(['GreenCar.png', 'BlueCar.png', 
                            'OrangeCar.png'])
    else:
        carColor = choice(['GreenCarReversed.png', 
                            'BlueCarReversed.png', 
                            'OrangeCarReversed.png'])
    if app.matrix[24][0] == 'road':
        numOfCars = randrange(3,4,5)
        for num in range(numOfCars):
            randCol = randrange(app.cols)
            app.carsList.append(car(24, randCol, carSpeed,carDirection, carColor))

def redrawAll(app):
    drawTerrain(app)
    drawLogs(app)
    drawTrees(app)
    drawCars(app)
    if not app.userScreen and not app.startingScreen:
        x, y = getCoord(app, app.player.row, app.player.col)
        drawImage(app.player.image, x, y)
        #draw score on left corner when game is playing 
        if not app.gameOver and not app.gamePaused:
            drawLabel(f'{app.score}', 40, 30, size = 50, bold = True, fill = 'white', border = 'black')
    #draw pause symbol when game is paused
    if app.gamePaused:
        drawRect(0, 0, app.width, app.height, fill = rgb(178, 255, 255), opacity = 65)
        drawRect(425, 250, 50, 100, fill = 'white', border = 'black')
        drawRect(525, 250, 50, 100, fill = 'white', border = 'black')
    #draw gameover screen including final score and leaderboard
    if app.gameOver:
        drawRect(0, 0, app.width, app.height, fill = rgb(234, 60, 83), opacity = 50)
        drawLabel('GAME OVER', app.width//2, 75, size = 40, bold = True, fill = 'white', border = 'black')
        drawLabel(f'Final Score: {app.score}', app.width//2, 130, size = 30, bold = True, fill = 'white', border = 'black')
        drawLabel('Press Any Key To Restart Game', app.width//2, 170, size = 20, bold = True, fill = 'white', border = 'black')
        drawRect(400, 200, 200, 300, fill = 'white', border = 'black')
        drawLabel('Current Leaderboard', app.width//2, 225, size = 15)
        drawLine(400, 250, 600, 250)
        drawLeaderboard(app)
    #draw starting screen when app first starts
    if app.startingScreen:
        drawLabel('CROSSY CODE', app.width//2, 170, size = 90, bold = True, fill = 'white', border = 'black')
        drawLabel('Press Any Key to Start', app.width//2, 400, size = 50, bold = True, fill = 'white', border = 'black')
    #draw bar to enter user name
    if app.userScreen:
        drawRect(0, 0, app.width, app.height, fill = rgb(178, 255, 255), opacity = 65)
        drawRect(300, 275, 400, 50, fill = 'white', border = 'black')
        drawLabel('Enter Username and Press Enter to Begin', app.width//2, 170, size = 30, bold = True, fill = 'black')
        drawLabel('User:', 330, app.height//2, size = 15)
        drawLabel(f'{app.user}', app.width//2, app.height//2, size = 15)

def drawTerrain(app):
    #terrain generation
    startXTerrain = -1 * app.tileSize * 13
    startYTerrain =  app.height / 2
    for row in range(app.rows):
        for col in range(app.cols):
            xTerrain = startXTerrain + col * app.tileSize + row * app.tileSize
            yTerrain = startYTerrain - row * app.tileSize//2 + col * app.tileSize//2
            if app.matrix[row][col] == 'grass':
                color = rgb(112,184,121)
            elif app.matrix[row][col] == 'river':
                color = rgb(169, 252, 254)
            else:
                color = rgb(84,87,98)
            drawPolygon(xTerrain, yTerrain + app.tileSize//2, 
                        xTerrain + app.tileSize, yTerrain, 
                        xTerrain + 2 * app.tileSize, yTerrain + app.tileSize//2, 
                        xTerrain + app.tileSize, yTerrain + app.tileSize,
                        fill = color)

def drawTrees(app):
    for trees in app.treesList:
        x, y = getCoord(app, trees.row, trees.col)
        drawImage(trees.image, x, y)

def drawLogs(app):
    for logs in app.logsList:
        x, y = getCoord(app, logs.row, logs.col)
        drawImage(logs.image, x - app.tileSize//2, y + app.tileSize//3)

def drawCars(app):
    for cars in app.carsList:
        x, y = getCoord(app, cars.row, cars.col)
        drawImage(cars.image, x, y + app.tileSize//3)

def drawLeaderboard(app):
    #sorts the scores in the txt file containing all previous scores
    sortedScore = []
    for scoreStr in app.leadtxt.splitlines():
        score = scoreStr.split(' ')[0]
        user = scoreStr.split(' ')[1]
        sortedScore.append((int(score), user))
    sortedScore = (sorted(sortedScore, reverse = True))
    #display the top 4 scores and your highest score at the bottom
    for i in range(4):
        points, name = sortedScore[i]
        drawLabel(f'{points}  =  {name}', app.width//2, 275 + 50 * i, size = 15)
        drawLine(400, 300 + 50 * i, 600, 300 + 50 * i)
    highscore = getHighScore(app, sortedScore)
    drawRect(400, 450, 200, 50, fill = 'yellow', border = 'black')
    drawLabel(f'Personal High =  {highscore}', app.width//2, 275 + 50 * 4, size = 15)

def getHighScore(app, sortedScore):
    for score in sortedScore:
        (points, name) = score
        if name == app.user:
            return points

def onKeyPress(app, key):
    if app.startingScreen:
        app.startingScreen = False
        app.userScreen = True
    if app.userScreen:
        if key == 'backspace':
            app.user = app.user[:-1]
        elif key == 'space':
            app.user += ' '
        elif key == 'enter':
            app.userScreen = False
        else:
            c = key
            app.user += c
    if app.gameOver:
        restart(app)
    if key == 'escape':
        app.gamePaused = not app.gamePaused
    if not app.gamePaused and not app.gameOver and not app.userScreen:
        #player cannot move into trees
        #gameover when player touches the river
        if (key == 'w' or key == 'up' or key == 'space') and not treeCollision(app, 'up'):
            if app.player.row >= 9: 
                shiftBoard(app)
                shift(app)
                app.score += 1
            app.player.up()
            if app.matrix[app.player.row][app.player.col] == 'river':
                if not logCollision(app):
                    app.gameOver = True
        if (key == "left" or key == 'a') and not treeCollision(app, 'left'):
            app.player.left()
            if app.matrix[app.player.row][app.player.col] == 'river':
                if not logCollision(app):
                    app.gameOver = True
        if (key == "right" or key == 'd') and not treeCollision(app, 'right'):
            app.player.right()
            if app.matrix[app.player.row][app.player.col] == 'river':
                if not logCollision(app):
                    app.gameOver = True
        if (key == "down" or key == 's') and not treeCollision(app, 'down'):
            app.player.down()
            if app.matrix[app.player.row][app.player.col] == 'river':
                if not logCollision(app):
                    app.gameOver = True

def treeCollision(app, direction):
    #checks if the next tile in the direction of the player has a tree
    row, col = app.player.row, app.player.col
    if direction == 'up':
        for trees in app.treesList:
            if trees.row == app.player.row + 1 and trees.col == app.player.col:
                return True
        return False
    elif direction == 'down':
        for trees in app.treesList:
            if trees.row == app.player.row - 1 and trees.col == app.player.col:
                return True
        return False
    elif direction == 'left':
        for trees in app.treesList:
            if trees.row == app.player.row and trees.col == app.player.col - 1:
                return True
        return False
    elif direction == 'right':
        for trees in app.treesList:
            if trees.row == app.player.row and trees.col == app.player.col + 1:
                return True
        return False
    
def logCollision(app):
    #checks after moving if on log or not
    for logs in app.logsList:
        if logs.row == app.player.row and logs.col == app.player.col:
            return logs.direction
    return False

def carCollision(app): 
    #checks if colliding with car or not
    for cars in app.carsList:
        if cars.row == app.player.row and cars.col == app.player.col:
            return True
    return False   

def onStep(app):        
    if app.gameOver and not app.store:
        app.leadtxt += f'{app.score} {app.user} \n'
        writeFile('lead.txt', app.leadtxt)
        app.store = True
    elif not app.gamePaused:
        if logCollision(app) == 'left': app.player.left()
        if logCollision(app) == 'right': app.player.right()
        for logs in app.logsList:
            if app.stepCount % logs.speed == 0:
                if logs.direction == 'left':
                    logs.left()
                else:
                    logs.right()
        
        for cars in app.carsList:
            if app.stepCount % cars.speed == 0:
                if cars.direction == 'left':
                    cars.left()
                else:
                    cars.right()
        if carCollision(app):
            app.gameOver = True

def main():
    runApp()
main()