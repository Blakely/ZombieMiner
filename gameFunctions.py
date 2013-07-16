#Filename: gameFunctions.py
#Author: Ryan Blakely
#Last Modified By: Ryan Blakely
#Last Modified: July 15th, 2013
#Description: Functions required for the ZombieMiner.py game


import pygame
from pygame.locals import *

from gameConstants import *

#initialize pygame
pygame.init()
#dirty fix to allow loading of images before main display kicks in
pygame.display.set_mode((1,1), pygame.NOFRAME)

#Generic load image function - loads an image from a file and sets its colorkey if given
#imgFile (str) - the filename for the image
#transColor (color) - the color wished to be transparent
#returns - the image (pygame Surface)
def loadImage(imgFile,transColor=None):
    #load image from file
    img = pygame.image.load(imgFile)
    
    #if there is a transparency color set, set the colorkey so that color is transparent
    if(transColor):
        #img=img.convert() #transparency fix for some images - converts it so it doesnt have a per-pixel alpha. not currently used
        img.set_colorkey(transColor, RLEACCEL)
    
    return img

#Creates an image from text
#text (str) - text to convert to an image
#font (pygame Font) - Font to be used in the image
#color (Color) - color of text
#transColor (Color) - for text transparency...not currently used
#returns - the text as an image (pygame Surface)
def textImage(text,font,color,transColor=None):
    if(transColor): #if theres a transparency set (never used currently - looks like crap)
        #create the text image from the font with the given transpaency colorkey
        txtImg=font.render(text, 1, color, transColor)
        txtImg.set_colorkey(transColor, RLEACCEL) #try to get rid of any remaining transparency color that may remain
    else: #otherwise, render it with bit transparency
        txtImg=font.render(text, 1, color)
        
    return txtImg

#Checks a given position value from a UI element to determine if it needs any special UI alignments in regards to its container
#pos (tuple) - the position to check for special UI flags
#bigSize (tuple) - the size of the container of the UI element
#smallSize (tuple) - the size of the UI element
#returns - either the original position if no UI alignment changes needed to occur, or the fixed positions for UI alignment
def specialPos(pos,bigSize,smallSize):
    #if the x position is meant to be "centered", center it
    if (pos[X]==ALIGN_CENTER):
        newPos = (bigSize[X]/2.0 - smallSize[X]/2.0,pos[Y]) #force float divison
    else:
        newPos = pos
    
    #if the y pos is meant to be "centered", center it
    if (pos[Y]==ALIGN_CENTER):
        newPos = (newPos[X],bigSize[Y]/2.0 - smallSize[Y]/2.0) #force float divison

    #elseif the y pos is meant to be "bottomed", put it at the bottom of the container
    elif (pos[Y]==ALIGN_BOTTOM):
        newPos = (newPos[X],bigSize[Y]-smallSize[Y])
        
    return newPos; 