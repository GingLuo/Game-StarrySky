# This is the main entry of the game.
import numpy as np
import random
from asteroid import Asteroid
import physics
import math
from cmu_112_graphics import *
from boids import *
import os
import time
from perlinNoise import *
from simpleNoise import *
from PIL import ImageEnhance
import pygame

######################################################################################################
# Notice:
#
# 1. All rgb values are referenced from here:
# http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
#
# 2. I referenced the graphics part taught in cmu 15-112:
# https://www.cs.cmu.edu/~112/notes/notes-graphics.html
# https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
#
# 3.I referenced the tkinter documentation:
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
#
# 4. The origianl inspiration of my game comes from the Kreator:
# https://apps.apple.com/us/app/the-kreator/id1464854122
#
# 5. People:
# TP Developer: Yichuan Luo (yichuanl)
# TP Mentor: Lauren Sands (lsands)
# 
######################################################################################################


#######################################################################################################
# Helper Functions
#######################################################################################################
# almostEqual is directly referenced from CMU website
# https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html#FloatingPointApprox
def almostEqual(d1, d2, epsilon=10**-7):
    return (abs(d2 - d1) < epsilon)

# Independent work
# This function determines a blue color with an input of (-1,1) float
def determineColor(num):
    # suppose num is 0.3456789
    # r_fact = 0.34, g_fact = 0.56, b_fact = 0.78
    # r in (75, 125), g in (150, 200), b in (150, 255)
    r_fact = num*100//1
    g_fact = num*10000//100
    b_fact = num*1000000//10000
    r_fact, g_fact, b_fact = r_fact/100, g_fact/100, b_fact/100
    r = 50 + int(50*r_fact)
    g = 160 + int(50*g_fact)
    b = 150 + int(105*b_fact)
    return (r, g, b)

# helper function that checks whether the input color is within range
def checkInvalidColor(color):
    if color <= 0:
        color = 0
    elif color >= 255:
        color = 255
    return color

# Graphic helper function to draw a rounded rectangle
# The way to draw a rounded rectangle is adaped from here:
# https://www.javaer101.com/en/article/16536652.html
def drawRoundedRectangle(canvas, x1, y1, x2, y2, **kwargs):
    radius = 25
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    canvas.create_polygon(points, **kwargs, smooth=True)

# Graphic function that draws the button
# Active image and activeText are from tkinter documentation:
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
def drawSettingBtn(app, canvas):
    margin = 20
    length = 80
    x1, y1 = app.width-margin-length, margin
    x2, y2 = app.width-margin, margin+length
    cx, cy = (x1+x2)//2,(y1+y2)//2
    margin = 50

    canvas.create_image(cx, cy, image=ImageTk.PhotoImage(app.buttonImg), 
                        activeimage=ImageTk.PhotoImage(app.activeButtonImg))

# helper function that detects a click on to the button
def onclickSettingBtn(app, event):
    # Parameter of the setting button
    margin = 5
    length = 80
    x1, y1 = app.width-margin-length, margin
    x2, y2 = app.width-margin, margin+length
    if (x1<=event.x<=x2 and y1<=event.y<=y2):
        app.openSetting = not app.openSetting

# graphic function that draws the sound bar
def drawSoundBar(app, canvas, x1, y1):
    num = 10
    margin = 10
    width = 8
    height = 20
    for i in range(num):
        leftX = x1+i*width+i*margin
        canvas.create_rectangle(leftX, y1, leftX+width, y1+height, fill="gray83", width=3,  outline="gray64")
        

# https://www.pygame.org/docs/ref/music.html
# Music is Refrain: https://www.youtube.com/watch?v=7qehStg7EB8
def onclickSoundBar(app, event, x1, y1):
    margin = 10
    width = 8
    height = 20
    x2 = x1+10*(width+margin)
    y2 = y1+height
    if (x1<event.x<x2) and (y1<event.y<y2):
        col = (event.x - x1) // (margin+width)
        newVol = col*10
        app.volume = int(newVol)
        pygame.mixer.music.set_volume(app.volume)       
        app.showSoundBar = False
        app.openSetting = False

#######################################################################################################
# Main App
#######################################################################################################
def appStarted(app):
    app.scale = 1/8
    app.gravityConstant = 0.5
    app.gravitationalConstant = 0.0001
    app.timerDelay = 100
    app.netForce = np.array([0,0])
    app.time0 = time.time()
    app.gameOver = False
    app.maxEnemy = 13
    app.recordList = []
    app.curPath = "TP/resources"

    # parameter of the earth planet
    app.er = 5000
    app.ex,app.ey = 0.5*app.width, 0.5*app.height+app.er
    app.em = 10000000000
    app.earth = Asteroid("Earth", app.ex, app.ey, app.er, app.em)

    # parameter of the player
    app.r = 20
    app.x, app.y = 0.5*app.width, 0.5*app.height-app.r
    app.mass = 1
    app.player = Asteroid("Player", app.x, app.y, app.r, app.mass)

    # parameter of food
    app.perDegree = 2
    app.indexSpeed = 1/20 
    app.totalMonster = 4
    app.flockList = []
    app.angleList = []
    app.accumulator = 0.5
    newFlockList(app)
    app.counterEnemy = 0
    app.counterMass = 0

    # paraeter of sprite
    app.initialSprites = []
    app.playerSprites = []
    makePlayerSprites(app)
    makeInitialSprites(app)
    app.playerSpriteCounter = 0
    app.initialSpriteCounter = 0

    # parametr of sky
    app.starTime = 0
    app.blinkTime = 0
    app.time0OfStar = time.time()
    app.time0OfBlink = time.time()
    app.starLineLists = []
    app.starSight = 250
    app.pixelLength = 10 # [200, 1800] -> row, col [20, 180], t
    app.pixelX, app.pixelY = 180, 20
    app.starPerlin = simpleNoiseFactory(3, app.pixelX, app.pixelY)
    setBlinkingSky(app)
    setStarrySky(app)
    updateStarLine(app)

    # parameter of background
    app.backgroundPerlin = PerlinNoiseFactory(2)
    app.resolution = 40
    setBackgroundPerlin(app)

    # the way I change its brightness is from PIL documentation:
    # https://omz-software.com/pythonista/docs/ios/ImageEnhance.html
    # The blue gear png is from here:
    # https://588ku.com/ycpng/12234755.html
    app.mode = 'indexPage'
    app.isPaused = False
    app.openSetting = False
    app.buttonImg = app.loadImage(app.curPath + '/Blue Setting Button.png')
    app.buttonImg = app.scaleImage(app.buttonImg, 1/13)
    enhancer = ImageEnhance.Brightness(app.buttonImg)
    app.buttonImg = enhancer.enhance(0.9)
    app.activeButtonImg = enhancer.enhance(1)
    app.showSoundBar = False

    app.indexPageMenu = setMenuParamters(app, "Menu",  "Sound", "Acknowledgement", "Record", "Back", "Exit")
    app.storyModeMenu = setMenuParamters(app, "Menu", "Back to Menu", "Sound", "Back")
    app.gameModeMenu = setMenuParamters(app, "Menu", "Back to Menu", "Sound", "Pause", "Restart", "Back", "Exit")

    # some animations
    app.hasPlayedIntroAnimation = False
    app.gameModeTransition = False
    app.storyModeTransition = False
    app.canDrawAck = False
    app.canDrawRecord = False
    app.transitionAngle = 0
    # The earth PNG is from here:
    # https://pngtree.com/freepng/earth-day-green-cute-earth-download_4673025.html?sce=sol_pin
    # I use Pil to open the image to rotate it later
    app.introImg = Image.open(app.curPath + '/Cute Earth.png')
    app.introImg = app.scaleImage(app.introImg, 1/5)
    app.introAngle = 0
    app.ackMessage = '''\
    Thanks Lauren for being the best TP mentor and giving me lots of awesome advice!
    I also want to acknowledge Prof. Kosbie and Taylor for the wonderful 15-112 course,\
    and all the TAs who answer questions lightning fast on piazza.
    Many thanks to my parents and my friends who stays up late with me in these weeks.   
    '''

    app.storyMessage = [
    'You', 
    'are a newly-born asteroid on a gigantic planet',
    'Fortunately',
    'the ominipotent god of starry sky casts the constellations as the Starry energy onto the ground',
    'You must adjust your position using your mouse',
    'Absorb the Starry energy and gain mass by bumping right into it',
    'Warning: There’re dangers behind you',
    'Any Starry energy ball you miss will become your enemy',
    'The god of starry sky will be pissed off if you miss a lot',
    'And that is BAD',
    'Remember the rule: ',
    'Eat the food, don’t get caught by the enemy, and Survive!']
    app.displayMessageIndex = 0
    app.storyControlT0 = time.time()
    app.storyIsOver = False

    app.enemy = Asteroid("Enemy", 0, 380, 15, 0)
    app.enemyList = []
    app.enemyBaseSpeed = 1
    app.playerDialogue = ['', 'You never catch me!', "That's a close one", 'Ohhh Noooo!', 'Almost Winning :)']
    app.enemyDialogue = ['', 'It sucks', 'Woo-hoo', 'I am here watching you always!']
    app.playerDialogueIndex = 0
    app.enemyDialogueIndex = 0
    app.playerDialogueTimer = time.time()
    app.enemyDialogueTimer = time.time()

    # background music parameters
    pygame.mixer.init()
    pygame.mixer.music.load(app.curPath + '/Refrain.mp3')
    pygame.mixer.music.play()
    app.volume = 50



# function that sets up the menus
def setMenuParamters(app, *args):
    newDict = {}
    menuWidth, menuHeight = 800, 500
    margin = 20
    buttonNumber = len(args) - 1
    buttonWidth, buttonHeight = menuWidth-2*margin, (menuHeight-(buttonNumber+1)*margin)//buttonNumber
    cx, cy = app.width/2, app.height/2
    cornerX, cornerY = cx-menuWidth//2, cy-menuHeight//2
    newDict["Menu"] = [cx-menuWidth//2, cornerY, cx+menuWidth//2, cornerY]
    
    # put the button and its corresponding positions into a dictionary
    for index in range(1, len(args)):
        text = args[index]
        prevText = args[index-1]
        newDict[text] = [cornerX+margin, (newDict[prevText][3]+margin),
                                    cornerX+margin+buttonWidth, (newDict[prevText][3]+margin+buttonHeight)]
    newDict["Menu"] = [cx-menuWidth//2, cy-menuHeight//2, cx+menuWidth//2, cy+menuHeight//2]

    return newDict

#####################################################################################################################
# Index Page                                                                                                        #
#####################################################################################################################
def indexPage_timerFired(app):
    app.introAngle += 20
    if (app.introAngle >= 360):
        app.hasPlayedIntroAnimation = True

    if (app.gameModeTransition):
        app.transitionAngle += 60
        if (app.transitionAngle >= 360):
            app.gameModeTransition = False
            app.mode = "gameMode"
            app.transitionAngle = 0
    
    if (app.storyModeTransition):
        app.transitionAngle += 60
        if (app.transitionAngle >= 360):
            app.storyModeTransition = False
            app.mode = "storyMode"
            app.transitionAngle = 0

# redrawAll function of indexPage
def indexPage_redrawAll(app, canvas):
    drawBackground(app, canvas)
    if (app.gameModeTransition == True) or (app.storyModeTransition == True):
        rotateEarth(app, canvas)
    elif (app.hasPlayedIntroAnimation == False):
        drawWelcomeAnimation(app, canvas)
    else:
        drawEarthBackground(app, canvas)
        if (app.openSetting == True):
            drawSettingBtn(app, canvas)
            drawIndexMenu(app, canvas)
        elif (app.canDrawAck == True):
            drawAcknowledgement(app, canvas)
        elif (app.canDrawRecord == True):
            drawRecord(app, canvas)
        else:
            drawSettingBtn(app, canvas)
            drawIndexPage(app, canvas)

# function that draws the welcome animation
def drawWelcomeAnimation(app, canvas):
    # Starry Planet
    canvas.create_text(app.width/2, app.height*0.2, text="Starry Planet", font="Verdana 50 bold", 
                       fill="DarkSlateGray4")
    
    
    rotateEarth(app, canvas)
    canvas.create_text(app.width*0.8, app.height*0.8, text="Produced by Ging Luo (yichuanl)", font="Verdana 10 bold", 
                       fill="dark slate gray")

    # Too ugly, No longer use it
    # fireImg = app.scaleImage(app.playerSprites[0], 1/2)
    # canvas.create_image(app.width/2, app.height*0.4 + 20*math.sin(2*np.radians(app.introAngle)), image=ImageTk.PhotoImage(fireImg))

# function that rotates an image
def rotateEarth(app, canvas):
    # The way I rotate my image is adapted from here:
    # https://www.daniweb.com/programming/software-development/threads/358903/rotating-canvas-item-tkinter
    img = app.introImg.rotate(app.introAngle)
    canvas.create_image(app.width/2, app.height*0.6, image=ImageTk.PhotoImage(img))

# function that draws the main features of the index page
def drawIndexPage(app, canvas):
    x1, y1 = app.width*0.5, app.height*0.2
    x2, y2 = app.width*0.5, app.height*0.35
    canvas.create_text(x1, y1, text="New Voyage!", font="Verdana 30 bold", 
                       fill="DarkSlateGray4", activefill="dark slate gray")
    canvas.create_text(x2, y2, text="Want a story?", font="Verdana 30 bold", 
                       fill="DarkSlateGray4", activefill="dark slate gray")


# function that draws the menu for index page
def drawIndexMenu(app, canvas):
    x1, y1 = app.indexPageMenu["Menu"][0], app.indexPageMenu["Menu"][1]
    x2, y2 = app.indexPageMenu["Menu"][2], app.indexPageMenu["Menu"][3]
    drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="gray83", width=3, outline="gray64")
    for key in app.indexPageMenu:
        if (key != "Menu"):
            x1, y1 = app.indexPageMenu[key][0], app.indexPageMenu[key][1]
            x2, y2 = app.indexPageMenu[key][2], app.indexPageMenu[key][3]
            drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="powder blue", width=3, outline="gray34")
            if (key == "Sound" and app.showSoundBar == True):
                xOffset = x1 + (x2-x1) * 0.4
                yOffset = y1 + (y2-y1) * 0.5 - 10
                drawSoundBar(app, canvas, xOffset, yOffset)
                canvas.create_text(x1 + (x2-x1) * 0.8, y1 + (y2-y1) * 0.5, text=f'Vol is {app.volume}', 
                                   font="Verdana 12 bold", fill="DarkSlateGray4")
                continue
            canvas.create_text((x1+x2)/2,(y1+y2)/2,text=key, font="Verdana 20 bold", 
                                fill="DarkSlateGray4", activefill="dark slate gray")

# mousePressed function of index page
def indexPage_mousePressed(app, event):
    if (app.openSetting == True):
        onclickIndexMenu(app, event)
        onclickSettingBtn(app, event)
    elif (app.canDrawAck == True):
        onclickAck(app, event)
    elif (app.canDrawRecord == True):
        onclickRecord(app, event)
    else:
        onclickSettingBtn(app, event)
        onclickIndexPage(app, event)

# function that detacts user's clicks to the main index page
def onclickIndexPage(app, event):
    x1, y1 = app.width*0.5, app.height*0.2
    x2, y2 = app.width*0.5, app.height*0.35
    if (x1-180<=event.x<=x1+180 and y1-30<=event.y<=y1+30):
        app.gameModeTransition = True
    elif (x2-190<=event.x<=x2+190 and y2-30<=event.y<=y2+30):
        app.storyModeTransition = True
        app.storyIsOver = False
        app.storyControlT0 = time.time()
        app.displayMessageIndex = 0


# function that draws the ack
def drawAcknowledgement(app, canvas):
    width, height = 800, 500
    leftX, leftY = app.width/2-width/2, app.height/2-height/2
    rightX, rightY = app.width/2+width/2, app.height/2+height/2
    drawRoundedRectangle(canvas, leftX, leftY, rightX, rightY, fill="Lightcyan2", width=3, outline="gray64")
    textWidthMargin = 80
    textHeightMargin = 100
    textSpacing = 100
    lineList = app.ackMessage.splitlines()
    for i in range(len(lineList)):
        text = lineList[i]
        canvas.create_text((leftX+rightX)/2, leftY+textSpacing*i+textHeightMargin, text=text, font="Verdana 14", 
                        fill="DarkSlateGray4", width=rightX-leftX-2*textWidthMargin)
    
    # Draw the X button
    margin = 30
    drawRoundedRectangle(canvas,rightX-margin, leftY, rightX, leftY+margin,
                         fill="gray83", width=2, outline="gray64")
    canvas.create_text(rightX-margin/2,leftY+margin/2,text="X",font="Verdana 20",
                        fill="LightBlue4", activefill="LightBlue3")

def drawRecord(app, canvas):
    width, height = 800, 500
    leftX, leftY = app.width/2-width/2, app.height/2-height/2
    rightX, rightY = app.width/2+width/2, app.height/2+height/2
    drawRoundedRectangle(canvas, leftX, leftY, rightX, rightY, fill="Lightcyan2", width=3, outline="gray64")
    textWidthMargin = 80
    textHeightMargin = 100
    textSpacing = 100
    lineList = app.recordList
    for i in range(len(lineList)):
        text = lineList[i]
        canvas.create_text((leftX+rightX)/2, leftY+textSpacing*i+textHeightMargin, text=text, font="Verdana 14", 
                        fill="DarkSlateGray4", width=rightX-leftX-2*textWidthMargin)
    
    # Draw the X button
    margin = 30
    drawRoundedRectangle(canvas,rightX-margin, leftY, rightX, leftY+margin,
                         fill="gray83", width=2, outline="gray64")
    canvas.create_text(rightX-margin/2,leftY+margin/2,text="X",font="Verdana 20",
                        fill="LightBlue4", activefill="LightBlue3")

def onclickAck(app, event):
    width, height = 800, 500
    leftX, leftY = app.width/2-width/2, app.height/2-height/2
    rightX, rightY = app.width/2+width/2, app.height/2+height/2
    margin = 30
    if (rightX-margin <= event.x <= rightX) and ( leftY <= event.y <= leftY+margin):
        app.canDrawAck = False

def onclickRecord(app, event):
    width, height = 800, 500
    leftX, leftY = app.width/2-width/2, app.height/2-height/2
    rightX, rightY = app.width/2+width/2, app.height/2+height/2
    margin = 30
    if (rightX-margin <= event.x <= rightX) and ( leftY <= event.y <= leftY+margin):
        app.canDrawRecord = False

# function that detacts user's click to menu
def onclickIndexMenu(app, event):
    # Parameters of the menu
    menuWidth, menuHeight = 800, 500
    margin = 20
    buttonNumber = 4
    buttonWidth, buttonHeight = menuWidth-2*margin, (menuHeight-(buttonNumber+1)*margin)//buttonNumber
    cx, cy = app.width/2, app.height/2
    cornerX, cornerY = cx-menuWidth//2, cy-menuHeight//2

    if (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
        app.indexPageMenu["Acknowledgement"][1]<=event.y<=app.indexPageMenu["Acknowledgement"][3]):
        app.canDrawAck = True
        app.openSetting = False
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.indexPageMenu["Sound"][1]<=event.y<=app.indexPageMenu["Sound"][3]):
        x1, x2 = cornerX+margin, cornerX+margin+buttonWidth
        y1, y2 = app.indexPageMenu["Sound"][1], app.indexPageMenu["Sound"][3]
        xOffset = x1 + (x2-x1) * 0.4
        yOffset = y1 + (y2-y1) * 0.5 - 10
        if(app.showSoundBar == True):
            onclickSoundBar(app, event, xOffset, yOffset)
        else:
            app.showSoundBar = True
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.indexPageMenu["Record"][1]<=event.y<=app.indexPageMenu["Record"][3]):
        app.canDrawRecord = True
        app.openSetting = False
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.indexPageMenu["Exit"][1]<=event.y<=app.indexPageMenu["Exit"][3]):
        app.quit()
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.indexPageMenu["Back"][1]<=event.y<=app.indexPageMenu["Back"][3]):
        app.openSetting = False

#####################################################################################################################
# Story Mode                                                                                                        #
#####################################################################################################################
# redrawAll function for story mode
def storyMode_redrawAll(app, canvas):
    if not app.storyIsOver:
        canvas.create_rectangle(-1,-1,app.width+1,app.height+1,
                                        fill="gray13",width=0)
        drawStoryAnimation(app, canvas)
    else:
        drawBackground(app, canvas)
        drawEarthBackground(app, canvas)

    drawSettingBtn(app, canvas)
    if (app.openSetting == True):
        drawStoryMenu(app, canvas)

# timerFired function for storyMode
def storyMode_timerFired(app):
    if app.storyIsOver: return
    if (time.time() - app.storyControlT0 >= 3):
        app.displayMessageIndex += 2
        app.storyControlT0 = time.time()
        if app.displayMessageIndex >= len(app.storyMessage):
            app.storyIsOver = True

# drawStory animation for story mode
def drawStoryAnimation(app, canvas):
    message1 = app.storyMessage[app.displayMessageIndex]
    message2 = app.storyMessage[app.displayMessageIndex+1]
    canvas.create_text(app.width/2, app.height*0.4, text=message1, font="Verdana 26 bold", 
                                fill="white", activefill="dark turquoise", width=app.width*0.8, justify="center")
    canvas.create_text(app.width/2, app.height*0.6, text=message2, font="Verdana 26 bold", 
                                fill="white", activefill="dark turquoise", width=app.width*0.8, justify="center")
        
# function that draws the menu
def drawStoryMenu(app, canvas):
    x1, y1 = app.storyModeMenu["Menu"][0], app.storyModeMenu["Menu"][1]
    x2, y2 = app.storyModeMenu["Menu"][2], app.storyModeMenu["Menu"][3]
    drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="gray83", width=3,  outline="gray64")
    for key in app.storyModeMenu:
        if (key != "Menu"):
            x1, y1 = app.storyModeMenu[key][0], app.storyModeMenu[key][1]
            x2, y2 = app.storyModeMenu[key][2], app.storyModeMenu[key][3]
            drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="powder blue", width=3, outline="gray34")
            if (key == "Sound" and app.showSoundBar == True):
                xOffset = x1 + (x2-x1) * 0.4
                yOffset = y1 + (y2-y1) * 0.5 - 10
                drawSoundBar(app, canvas, xOffset, yOffset)
                canvas.create_text(x1 + (x2-x1) * 0.8, y1 + (y2-y1) * 0.5, text=f'Vol is {app.volume}', 
                                   font="Verdana 12 bold", fill="DarkSlateGray4")
                continue
            canvas.create_text((x1+x2)/2,(y1+y2)/2,text=key, font="Verdana 20 bold", 
                                fill="DarkSlateGray4", activefill="dark slate gray")

# mousePressed function for storyMode
def storyMode_mousePressed(app, event):
    onclickSettingBtn(app, event)
    if (app.openSetting == True):
        onclickStoryMenu(app, event)

# function that detects user's click to the menu
def onclickStoryMenu(app, event):
    # Parameters of the menu
    menuWidth, menuHeight = 800, 500
    margin = 20
    buttonNumber = 4
    buttonWidth, buttonHeight = menuWidth-2*margin, (menuHeight-(buttonNumber+1)*margin)//buttonNumber
    cx, cy = app.width/2, app.height/2
    cornerX, cornerY = cx-menuWidth//2, cy-menuHeight//2

    if (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
        app.storyModeMenu["Back to Menu"][1]<=event.y<=app.storyModeMenu["Back to Menu"][3]):
        app.mode = 'indexPage'
        app.openSetting = False
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.storyModeMenu["Sound"][1]<=event.y<=app.storyModeMenu["Sound"][3]):
        x1, x2 = cornerX+margin, cornerX+margin+buttonWidth
        y1, y2 = app.storyModeMenu["Sound"][1], app.storyModeMenu["Sound"][3]
        xOffset = x1 + (x2-x1) * 0.4
        yOffset = y1 + (y2-y1) * 0.5 - 10
        if(app.showSoundBar == True):
            onclickSoundBar(app, event, xOffset, yOffset)
        else:
            app.showSoundBar = True
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.storyModeMenu["Back"][1]<=event.y<=app.storyModeMenu["Back"][3]):
        app.openSetting = False

#####################################################################################################################
# Game Mode                                                                                                         #
#####################################################################################################################
# Control functions of game mode
# keyPressed function for game mode
def gameMode_keyPressed(app, event):
    if(event.key == "s"):
        # Step
        # For debugging purpose
        for _ in range(10):
            gameMode_timerFired(app)

# mousePressed function for game mode
def gameMode_mousePressed(app, event):
    if (event.y > 0.5*app.height) and (app.openSetting == False):
        return
    defaultMass = 1000000000
    dVector = (np.array([event.x,event.y]) - app.player.pos)
    attractionForce = physics.gravitationalForce(
                app.player.mass, defaultMass, app.gravitationalConstant, dVector)
    app.netForce = np.add(app.netForce, attractionForce)
    onclickSettingBtn(app, event)
    if (app.openSetting == True):
        onclickGameMenu(app, event)
    if (app.gameOver):
        onclickGameOverPage(app, event)

# mouseReleased function for game modde
def gameMode_mouseReleased(app, event):
    app.netForce = 0
    app.player.vel = np.array([0,0])
    app.player.acc = np.array([0,0])

# function that detacts user's clicks to the main index page
def onclickGameOverPage(app, event):
    x1, y1 = app.width*0.5, app.height*0.2
    x2, y2 = app.width*0.5, app.height*0.35
    if (x1-180<=event.x<=x1+180 and y1-30<=event.y<=y1+30):
        tempList = app.recordList
        appStarted(app)
        app.mode = "gameMode"
        app.recordList = tempList
        app.hasPlayedIntroAnimation = True
    elif (x2-190<=event.x<=x2+190 and y2-30<=event.y<=y2+30):
        tempList = app.recordList
        appStarted(app)
        app.recordList = tempList



# function that detects user's click to the menu
def onclickGameMenu(app, event):
    # Parameters of the menu
    menuWidth, menuHeight = 800, 500
    margin = 20
    buttonNumber = 4
    buttonWidth, buttonHeight = menuWidth-2*margin, (menuHeight-(buttonNumber+1)*margin)//buttonNumber
    cx, cy = app.width/2, app.height/2
    cornerX, cornerY = cx-menuWidth//2, cy-menuHeight//2

    if (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
        app.gameModeMenu["Back to Menu"][1]<=event.y<=app.gameModeMenu["Back to Menu"][3]):
        app.mode = 'indexPage'
        app.openSetting = False
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.gameModeMenu["Exit"][1]<=event.y<=app.gameModeMenu["Exit"][3]):
        app.quit()
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.gameModeMenu["Sound"][1]<=event.y<=app.gameModeMenu["Sound"][3]):
        x1, x2 = cornerX+margin, cornerX+margin+buttonWidth
        y1, y2 = app.gameModeMenu["Sound"][1], app.gameModeMenu["Sound"][3]
        xOffset = x1 + (x2-x1) * 0.4
        yOffset = y1 + (y2-y1) * 0.5 - 10
        if(app.showSoundBar == True):
            onclickSoundBar(app, event, xOffset, yOffset)
        else:
            app.showSoundBar = True

    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.gameModeMenu["Pause"][1]<=event.y<=app.gameModeMenu["Pause"][3]):
        app.isPaused = not app.isPaused
        if (app.isPaused):
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        app.openSetting = False
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.gameModeMenu["Restart"][1]<=event.y<=app.gameModeMenu["Restart"][3]):
        tempList = app.recordList
        appStarted(app)
        app.mode = "gameMode"
        app.recordList = tempList
        app.hasPlayedIntroAnimation = True
    elif (cornerX+margin<=event.x<=cornerX+margin+buttonWidth and 
          app.gameModeMenu["Back"][1]<=event.y<=app.gameModeMenu["Back"][3]):
        app.openSetting = False

# function that confines the user within the window scope
def boundary(app):
    if app.player.pos[0] <= 0:
        app.player.pos[0] = 1
    elif app.player.pos[0] >= app.width:
        app.player.pos[0] = app.width - 1

    if app.player.pos[1] <= 0:
        app.player.pos[1] = 1
    elif app.player.pos[1] >= app.height:
        app.player.pos[1] = app.height - 1

###############################################
# Computer graphic part: perlin and sprites
# The sprites are from here:
# http://www.6m5m.com/service-sid-32167.html
def makePlayerSprites(app):
    path = app.curPath + '/fire'
    for fileName in os.listdir(path):
        newImage = app.loadImage(path+'/'+fileName)
        newImage = app.scaleImage(newImage, 1/6)
        app.playerSprites.append(newImage)

def makeInitialSprites(app):
    path = app.curPath + '/initialFire'
    for fileName in os.listdir(path):
        newImage = app.loadImage(path+'/'+fileName)
        newImage = app.scaleImage(newImage, 1/6)
        app.initialSprites.append(newImage)

# The way I use Perlin noise below is adapted from here:
# https://www.redblobgames.com/maps/terrain-from-noise/
# Set the color for background
def setBackgroundPerlin(app):
    # (1600, 800) -> (160, 80)
    col = app.width//app.resolution
    row = app.height//app.resolution
    app.backgroundTileList = [[0]*col for _ in range(row)]
    for i in range(row):
        for j in range(col):
            ny = i/row-0.5
            nx = j/col-0.5
            
            val = app.backgroundPerlin.getPerlinVal(nx*3,ny*3)
            # Prestore the color
            (r, g, b) = determineColor(val)
            # slightly modify the color a little bit
            b += 15
            g += 10
            r = checkInvalidColor(r)
            g = checkInvalidColor(g)
            b = checkInvalidColor(b)
            color = f'#{r:02x}{g:02x}{b:02x}'
            app.backgroundTileList[i][j] = color
    
# Set the sky with constellations
def setStarrySky(app):
    app.starList = []
    for row in range(app.pixelY):
        for col in range(app.pixelX):
            ny = row/app.pixelY-0.25
            nx = col/app.pixelX-0.25
            num = app.starPerlin.getSimpleNoiseVal(nx*3, ny*3, app.starTime)
            if (int(num*1000)%100 == 6):
                app.starList.append((row, col, num))

# set the blinking stars
def setBlinkingSky(app):
    app.blinkList = []
    for row in range(app.pixelY):
        for col in range(app.pixelX):
            ny = row/app.pixelY-0.25
            nx = col/app.pixelX-0.25
            num = app.starPerlin.getSimpleNoiseVal(nx*3, ny*3, app.blinkTime)
            if (4 < int(num*1000)%100 < 7):
                blinktime = random.randint(5, 25)
                blinktime /= 10
                app.blinkList.append((row, col, num, blinktime))

# Independent work.
# reject sampling to generate good-looking star lines
def updateStarLine(app):
    app.starLineLists = []
    length = len(app.starList)
    totalNum = random.randint(4,7)
    
    for i in range(totalNum):
        lineList = []
        maxLength = 4-i//2
        prevIndex = random.randint(0, length-1)
        prevStar = app.starList[prevIndex]

        while(True):
            index = random.randint(0, length-1)
            newStar = app.starList[index]

            crow, ccol = prevStar[0], prevStar[1]
            cx = ccol*app.pixelLength
            cy = crow*app.pixelLength

            drow, dcol = newStar[0], newStar[1]
            dx = dcol*app.pixelLength
            dy = drow*app.pixelLength

            if (physics.distance(cx,cy,dx,cy)<app.starSight):
                lineList += [newStar]
                prevStar = newStar
            if (len(lineList)>=maxLength):
                break
        
        app.starLineLists.append(lineList)

###################################################
# Initiate Food
# This method comes from my own independent work
# Generate a new flock list with 4 new flocks
def newFlockList(app):
    
    # This will give me the height of each flock
    for index in range(app.totalMonster):
        index = index + len(app.flockList)
        if (app.angleList != []):
            newAngle = app.angleList[-1] + (index - len(app.flockList) + 1) * app.perDegree
        else:
            newAngle = index * app.perDegree
        
        degree = np.radians(newAngle)
        baseX, baseY = int(app.ex + math.sin(degree)*app.er), int(app.ey - math.cos(degree)*app.er)
        margin = 50
        perlinStep = index / app.totalMonster - 0.5
        radius = random.randint(30,50)
        # get a continuous height for food
        # increase the multiple will bring more variance as it takes a larger step
        bx1, bx2 = baseX - 1*margin, baseX + 1*margin
        by1, by2 = baseY - 2*margin, baseY + 2*margin
        
        while (True):
            cx = random.randint(bx1, bx2)
            cy = random.randint(by1, by2)
            if (physics.distance(cx, cy, app.ex, app.ey)>(radius+app.er)):
                break
        

        retVal = newFlock(app, cx, cy, radius)
        app.flockList.append(retVal)
        
        app.angleList.append(newAngle)

# Independent work
# Generate a new flock
def newFlock(app, cx, cy, radius):
    totalBoids = random.randint(2,4)
    flock = []
    identity = random.choice(["StaticFood", "DynamicFood"])

    cr = radius
    x = random.randint(cx-cr,cx+cr)
    y = cy - (cr**2-(cx-x)**2)**0.5

    velX = random.uniform(-2, 2)
    velY = random.uniform(-1.5, 1.5)
    vel = np.array([velX, velY])
    accX = random.uniform(-0.3,0.3)
    accY = random.uniform(-0.3,0.3)
    acc = np.array([accX, accY])

    # acc = (np.random.rand(2) - 0.5)*2
    direc = random.choice([-1,1])

    # loop that updates the flock
    for i in range(totalBoids):

        newBoid = Boid(identity,x,y, 5, 1, vel, acc, cx, cy, cr, direc)
        
        for _ in range(5*i):
            newBoid.update()

        if (newBoid.identity == "StaticFood"):
            newBoid.forbidUpdate = True
        
        flock.append(newBoid)

    return flock

############################################
# functions related to force
# independent work
# calculate the gravity
def gravity(app):
    gravity = physics.gravity(app.player.mass, app.gravityConstant)
    app.netForce = np.add(app.netForce, gravity)

# calculate the normal force
def normalForce(app):
    gravity = physics.gravity(app.player.mass, app.gravityConstant)
    normalForce = physics.normalForce(gravity)
    app.netForce = np.add(app.netForce, normalForce)

############################################
# This block contains time-related functions
# timerFired function that does the animation part
def gameMode_timerFired(app):
    if (app.isPaused == True):  return
    if(app.gameOver):   
        return
    collisionType = physics.detectRigidBodyCollision(app.player, app.earth)
    if (collisionType != False):
        bounce(app)        

    gravity(app)    
    app.player.applyForce(app.netForce, app.earth)
    app.player.update()
    boundary(app)
    app.netForce = 0

    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)
    app.initialSpriteCounter += 1
    
    # updates relevant parametrs when game over
    incoming(app)
    app.gameOver = checkGameOver(app)
    if(app.gameOver):
        curtime = time.ctime()
        L = curtime.split(" ")
        month = L[1]
        date = L[2]
        if (L[2] == ""):
            date = L[3]
            curTime = L[4]
        else:
            date = L[2]
            curTime = L[3]
        curTime = curTime[0:5]
        timeMessage = f'Voyage at {month}{date} {curTime}: '
        gameMessage = f'Got {app.counterMass} weight and died at {app.counterEnemy} enemies.'
        app.recordList.append(timeMessage+gameMessage)
    checkEatFood(app)
    enemyUpdate(app, 0)

    # updates parameters related to dialogue
    if app.playerDialogueIndex != 0:
        if (time.time() - app.playerDialogueTimer > 3):
            app.playerDialogueTimer = time.time()
            app.playerDialogueIndex = 0

    if app.enemyDialogueIndex != 0:
        if (time.time() - app.enemyDialogueTimer > 3):
            app.enemyDialogueTimer = time.time()
            app.enemyDialogueIndex = 0
    
    # updates the changing time of stars
    if time.time() - app.time0OfStar > 9:
        app.starTime += 0.01
        setStarrySky(app)
        updateStarLine(app)
        app.time0OfStar = time.time()
    if time.time() - app.time0OfBlink > 3:
        app.blinkTime += 0.01
        setBlinkingSky(app)
        app.time0OfBlink = time.time()

# independent work
# function that describes the collision process
def bounce(app):
    
    if(physics.detectRigidBodyCollision(app.player, app.earth) == None):
        x = app.player.pos[0]
        y = app.player.pos[1]
        ex,ey = app.earth.pos[0], app.earth.pos[1]
        while (((ex-x)**2 + (ey-y)**2)**0.5 < app.player.r+app.earth.r):
            y -= 0.1
        app.player.pos = np.array([x,y])
    physics.rigidBodyCollision(app.player, app.earth)
    normalForce(app)

# independent work
def checkEatFood(app):
    # updates the food
    for index in range(len(app.flockList)):
        flock = app.flockList[index]
        for item in flock:
            flag = physics.detectRigidBodyCollision(app.player, item)
            if ((flag == True) or (flag == None)) and (item.hasBeenEaten == False):
                if item.identity == "StaticFood" or item.identity == "DynamicFood":
                    app.counterMass += item.mass
                    item.hasBeenEaten = True
                    enemyUpdate(app, -0.5*app.enemyBaseSpeed)
    # Dialogue of the player
    if (time.time() - app.playerDialogueTimer > 5):
        if (app.player.pos[0] - app.enemy.pos[0] > 700):
            if (app.playerDialogueIndex != 1) and app.enemy.pos[0] > 30:
                app.playerDialogueIndex = 1
                app.playerDialogueTimer = time.time()
        elif (100<app.player.pos[0] - app.enemy.pos[0] < 250):
            app.playerDialogueIndex = 3
            app.playerDialogueTimer = time.time()
        elif (app.player.pos[0] - app.enemy.pos[0] < 100):
            app.playerDialogueIndex = 2
            app.playerDialogueTimer = time.time()
        elif (app.counterMass > 50):
            app.playerDialogueIndex = 4
            app.playerDialogueTimer = time.time()

# modify flockList, set the way the food is generated and moving
def incoming(app):

    # moving the food forward
    app.accumulator += app.indexSpeed
    for index in range(len(app.angleList)):
        app.angleList[index] -= app.perDegree * app.indexSpeed
        diff = int(app.angleList[index]) - app.angleList[index]
        if (abs(diff)<0.001):
            app.angleList[index] = int(app.angleList[index])
    
    # moving the food forward
    for index in range(len(app.flockList)):
        oldAngle = np.radians(app.angleList[index] - app.perDegree * app.indexSpeed)
        newAngle = np.radians(app.angleList[index])
        dx = (app.ex + math.sin(newAngle)*app.er) - (app.ex + math.sin(oldAngle)*app.er)
        dy = (app.ey - math.cos(newAngle)*app.er) - (app.ey - math.cos(oldAngle)*app.er)
        for boid in app.flockList[index]:
            boid.cx -= dx
            boid.cy -= dy
            boid.pos[0] -= dx
            boid.pos[1] -= dy

    # check and turns the food into enemy
    if (app.flockList[0][0].pos[0]<100):
        temp = app.flockList.pop(0)
        app.angleList.pop(0)
        for item in temp:
            item.hasBeenMoved = True
            if (item.hasBeenEaten == False):
                item.isEnemy = True
                app.counterEnemy += 1
                app.enemyList.append(item)
                mass = item.turnEnemy()
                app.enemy.mass += mass
                app.enemy.r += mass
                enemyUpdate(app, app.enemyBaseSpeed)
        app.accumulator = 0.5

    if (len(app.flockList)<=3):
        newFlockList(app)

    for flock in app.flockList:
        for item in flock:
            item.update()
            #item.acc += item.alignment(flock)
            #item.acc += item.cohesion(flock)
            item.acc += item.separation(flock)

# True for losing the game, False for continuing
def checkGameOver(app):
    if physics.detectRigidBodyCollision(app.enemy, app.player) != False:
        return True
    if app.enemy.pos[0] > app.player.pos[0]:
        return True
    counter = app.counterEnemy
    if (counter >= app.maxEnemy):
        return True
    return False

# updates the conditions of enemy
def enemyUpdate(app, v_mag):
    if app.enemy.pos[0] > 0 or v_mag > 0:
    
        # chase the player
        v_hat = app.player.pos - app.enemy.pos
        v_hat = np.divide(v_hat, np.linalg.norm(v_hat))
        newVel = v_hat * v_mag
        if newVel[1] > 0:
            y_crit = app.ey - (app.er**2 - (app.enemy.pos[0]-app.ex)**2)**0.5
            if (app.enemy.pos[1]>=y_crit):
                newVel[1] *= -1
                app.enemy.vel[1] *= -1
        app.enemy.vel = np.add(newVel, app.enemy.vel)
        app.enemy.pos = np.add(app.enemy.vel, app.enemy.pos)

        if (time.time() - app.enemyDialogueTimer > 5):
            if (np.linalg.norm(app.enemy.vel) > 4):
                app.enemyDialogueIndex = 2
                app.enemyDialogueTimer = time.time()
            elif (-1 < np.linalg.norm(app.enemy.vel) < 1):
                if (app.enemyDialogueIndex != 1):
                    app.enemyDialogueIndex = 1
                    app.enemyDialogueTimer = time.time()
            elif (app.enemy.pos[0]<3):
                app.enemyDialogueIndex = 3
                app.enemyDialogueTimer = time.time()

        if app.enemy.pos[0] < 0:
            app.enemy.vel = np.array([0,0])


    # merge the enemy into a bigger one
    for boid in app.enemyList:
        v_hat = app.enemy.pos - boid.pos
        v_hat = np.divide(v_hat, np.linalg.norm(v_hat))
        v_mag = 1
        vel = v_mag * v_hat
        boid.vel += vel
        boid.r += 0.05
        boid.pos = np.add(boid.vel, boid.pos)
        if physics.distance(boid.pos[0], boid.pos[1], app.enemy.pos[0], app.enemy.pos[1]) < app.enemy.r+15:
            boid.isMerged = True



############################################
# Graphic Part of the game mode
# draw stars that are blinking
def drawBlinkingStars(app, canvas):
    for (row, col, num, blinktime) in app.blinkList:
        cx = col*app.pixelLength
        cy = row*app.pixelLength
        if(time.time() - app.time0OfBlink < blinktime):
            (r, g, b) = determineColor(num)
            b -= 25
            g += 10
            r = checkInvalidColor(r)
            g = checkInvalidColor(g)
            b = checkInvalidColor(b)
            #(r, g, b) = (135,206,235)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_oval(cx-7,cy-8,cx,cy, width=0, fill=color)
        else:
            (r, g, b) = determineColor(num)
            r = checkInvalidColor(r)
            g = checkInvalidColor(g)
            b = checkInvalidColor(b)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_oval(cx-8,cy-7,cx,cy, width=0, fill=color)

# draw the constant stars that lasts longer
def drawStars(app, canvas):

    for (row, col, num) in app.starList:
        cx = col*app.pixelLength
        cy = row*app.pixelLength
        (r, g, b) = determineColor(num)
        r = checkInvalidColor(r)
        g = checkInvalidColor(g)
        b = checkInvalidColor(b)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_oval(cx-7,cy-7,cx,cy, width=0, fill=color)
    
    
    for item in app.starLineLists:
            drawStarLine(app, canvas, item)


# draws starlines that forms constellations
def drawStarLine(app, canvas, lineList):
    if(len(lineList) == 1 or len(lineList) == 0):
        return
    else:
        prevRow, prevCol = lineList[0][0], lineList[0][1]
        prevX = prevCol*app.pixelLength
        prevY = prevRow*app.pixelLength
        
        for i in range(1,len(lineList)):
            (row, col, num) = lineList[i]
            cx = col*app.pixelLength
            cy = row*app.pixelLength
            canvas.create_line(cx-2.5, cy-2.5, prevX-2.5, prevY-2.5, fill="LightBlue3", width=1)
            prevX, prevY = cx, cy

# draws sprites
def drawPlayerSprites(app, canvas, cx, cy):
    sprite = app.playerSprites[app.playerSpriteCounter]
    canvas.create_image(cx, cy, image=ImageTk.PhotoImage(sprite))

# draws initial sprites
def drawInitialSprites(app, canvas, cx, cy):
    sprite = app.initialSprites[app.initialSpriteCounter]
    canvas.create_image(cx, cy, image=ImageTk.PhotoImage(sprite))

# draw the player's figure, calls draw sprite
def drawPlayer(app, canvas):
    
    cx, cy, cr = app.player.pos[0], app.player.pos[1], app.player.r
    if (app.initialSpriteCounter >= len(app.initialSprites)):
        drawPlayerSprites(app, canvas, cx, cy-2)
    else:
        drawInitialSprites(app, canvas, cx, cy-2)
    canvas.create_oval(cx-cr,cy-cr,cx+cr,cy+cr, width=2, outline="gold")

# draws the food
def drawFlock(app, canvas):
    for flock in app.flockList:
        for item in flock:
            cx, cy = item.pos[0], item.pos[1]
            r = item.r
            if item.hasBeenEaten == True:
                pass
            else:
                canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="thistle1")
            # canvas.create_oval(item.cx-5,item.cy-5,item.cx+5,item.cy+5)    

# draws the enemy 
def drawEnemy(app, canvas):
    for item in app.enemyList:
        if item.isMerged == False:
            cx, cy = item.pos[0], item.pos[1]
            r = item.r
            canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="black")
    
    if (len(app.enemyList) == 0):   return
    r = app.enemy.r
    cx, cy = app.enemy.pos[0], app.enemy.pos[1]
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill="black")


# draws the dialogue of the player and the enemy
def drawDialogue(app, canvas):
    playerText = app.playerDialogue[app.playerDialogueIndex]
    enemyText = app.enemyDialogue[app.enemyDialogueIndex]
    # For the player
    if (playerText != ''):
        width, height = 13*len(playerText), 40
        leftX = app.player.pos[0] + app.player.r + 5
        rightY = app.player.pos[1] - app.player.r - 5
        leftY = rightY - height
        rightX = leftX + width
        drawRoundedRectangle(canvas, leftX, leftY, rightX, rightY, fill='', width=3, outline="gray64")
        canvas.create_text(leftX+width/2, leftY+height/2, text=playerText, font="Verdana 10 bold", 
                        fill="DarkSlateGray4")


    # For the enemy
    if (enemyText != ''):
        width, height = 13*len(enemyText), 40
        leftX = app.enemy.pos[0] + app.player.r + 5
        rightY = app.enemy.pos[1] - app.player.r - 5
        leftY = rightY - height
        rightX = leftX + width
        drawRoundedRectangle(canvas, leftX, leftY, rightX, rightY, fill='', width=3, outline="gray64")
        canvas.create_text(leftX+width/2, leftY+height/2, text=enemyText, font="Verdana 10 bold", 
                        fill="DarkSlateGray4")
    

# The use of stipple to get a transparency is referenced from here
# https://piazza.com/class/kjyble3m9l1ar?cid=3558
def drawEarthBackground(app, canvas):
    ex, ey, er = app.earth.pos[0], app.earth.pos[1], app.earth.r
    canvas.create_oval(ex-er,ey-er,ex+er,ey+er, width=6)
    
    # when I put a return here, the performance looks good
    # Draw the major part of the earth
    for row in range(len(app.backgroundTileList)//2+2,len(app.backgroundTileList)):
        for col in range(len(app.backgroundTileList[0])):
            color = app.backgroundTileList[row][col]
            cx = col*app.resolution
            cy = row*app.resolution
            canvas.create_rectangle(cx,cy,cx+app.resolution,cy+app.resolution,
                                    fill=color,width=0, stipple='gray75')
    
    # when I put a return here, the performance looks a little bit slow
    # Draw the irregular part of the earth
    row = len(app.backgroundTileList)//2
    for col in range(len(app.backgroundTileList[0])):
        color = app.backgroundTileList[row+2][col]
        x1 = col*app.resolution
        x2 = col*app.resolution + app.resolution
        heightOffset = row*app.resolution+ 2*app.resolution
        drawInfinitesimalSlice(app, canvas, x1,x2,heightOffset, color, 20)

    # when I put a return here, the performance is very slow

# Draws infinitesimal rectangles that fills up a region with a arc as its upbound
def drawInfinitesimalSlice(app, canvas, x1, x2, heightOffset, color, step=1):
    # arc is the upper bound of app.earth
    for cx in range(x1, x2, step):
        cy = app.ey - (app.er**2 - (cx-app.ex)**2)**0.5 
        canvas.create_rectangle(cx, cy, cx+step, heightOffset, fill=color, width=0, stipple='gray75')


# draws the whole light blue backgroud
def drawBackground(app, canvas):
    canvas.create_rectangle(-1,-1,app.width+1,app.height+1,
                                    fill="powder blue",width=0, stipple='gray50')

# draws the menu for gameMode
def drawGameMenu(app, canvas):
    x1, y1 = app.gameModeMenu["Menu"][0], app.gameModeMenu["Menu"][1]
    x2, y2 = app.gameModeMenu["Menu"][2], app.gameModeMenu["Menu"][3]
    drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="gray83", width=3,  outline="gray64")
    for key in app.gameModeMenu:
        if (key != "Menu"):
            x1, y1 = app.gameModeMenu[key][0], app.gameModeMenu[key][1]
            x2, y2 = app.gameModeMenu[key][2], app.gameModeMenu[key][3]
            drawRoundedRectangle(canvas,x1, y1, x2, y2, fill="powder blue", width=3, outline="gray34")
            if (key == "Sound" and app.showSoundBar == True):
                xOffset = x1 + (x2-x1) * 0.4
                yOffset = y1 + (y2-y1) * 0.5 - 10
                drawSoundBar(app, canvas, xOffset, yOffset)
                canvas.create_text(x1 + (x2-x1) * 0.8, y1 + (y2-y1) * 0.5, text=f'Vol is {app.volume}', 
                                   font="Verdana 12 bold", fill="DarkSlateGray4")
                continue
            canvas.create_text((x1+x2)/2,(y1+y2)/2,text=key, font="Verdana 20 bold", 
                                fill="DarkSlateGray4", activefill="dark slate gray")

# draws the counter
def drawCounter(app, canvas):
    canvas.create_text(100, 250, text=f'Enemy: {app.counterEnemy}', font="Verdana 14 bold", 
                       fill="DarkSlateGray4")
    canvas.create_text(100, 300, text=f'Mass: {app.counterMass}', font="Verdana 14 bold", 
                       fill="DarkSlateGray4")

# draws gameOver message and options
def drawGameOver(app, canvas):
    canvas.create_text(app.width//2, app.height//2+100, text=f'You Lose. Total Mass={app.counterMass}', font="Verdana 50 bold", 
                       fill="indian red")
    x1, y1 = app.width*0.5, app.height*0.2
    x2, y2 = app.width*0.5, app.height*0.35
    canvas.create_text(x1, y1, text="Try Again?", font="Verdana 30 bold", 
                       fill="DarkSlateGray4", activefill="dark slate gray")
    canvas.create_text(x2, y2, text="Back to Menu?", font="Verdana 30 bold", 
                       fill="DarkSlateGray4", activefill="dark slate gray")




# redrawAll function for the gameMode
def gameMode_redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawEarthBackground(app, canvas)
    if not app.gameOver:
        drawPlayer(app, canvas)
        drawFlock(app, canvas)
        drawEnemy(app, canvas)
        drawBlinkingStars(app, canvas)
        drawStars(app, canvas)
        drawCounter(app, canvas)
        drawDialogue(app, canvas)
    else:
        drawGameOver(app, canvas)

    drawSettingBtn(app, canvas)
    if (app.openSetting == True):
        drawGameMenu(app, canvas)

    

#####################################################################################################################
runApp(width=1800, height=800)

