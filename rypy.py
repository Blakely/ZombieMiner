import pygame
from pygame.locals import *

X=0
Y=1

#Generic load image function
def loadImage(imgFile,transColor=None):
    #load image from file
    img = pygame.image.load(imgFile)
    
    if(transColor):
        #img=img.convert() #transparency fix for some images - converts it so it doesnt have a per-pixel alpha
        img.set_colorkey(transColor, RLEACCEL)
    
    return img

#Generic pixel-by-pixel RGB changer for a Surface
def changeRGB(img,factor):
    for y in range(img.get_height()):
        for x in range(img.get_width()):
            pixel = img.get_at((x,y))
            if (pixel!=img.get_colorkey()):
                red = int(factor * pixel.r)
                green = int(factor * pixel.g)
                blue = int(factor * pixel.b)
                img.set_at((x,y),(red,green,blue))
                
CENTER=-1

def centered(pos,bSize,sSize):
    #if the x position is meant to be "centered", center it
    if (pos[X]==CENTER):
        newPos = (bSize[X]/2 - sSize[X]/2,pos[Y])
    else:
        newPos = pos
    
    #if the y pos is meant to be "centered", center it
    if (pos[Y]==CENTER):
        newPos = (newPos[X],bSize[Y]/2 - sSize[Y]/2)
        
    return newPos; 

def textImage(text,font,color,transColor=None):
    if(transColor):
        txtImg=font.render(text, 1, color, transColor)
        txtImg.set_colorkey(transColor, RLEACCEL)
    else:
        txtImg=font.render(text, 1, color)
        
    return txtImg

#Generic graphical object              
class Drawable(object):
    def __init__(self, pos=(0,0),img=None):
        self.pos = pos
        self.img = None
        
        if(img):
            self.img = img.copy()
            self.size = img.get_size()
        
    def draw(self,screen,offsetPos=(0,0)):
        if(self.img):
            screen.blit(self.img,(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y]))
    
    def click(self,mousePos):
        if(self.img):
            if (self.pos[X]<mousePos[X] and self.pos[X]+self.size[X]>mousePos[X]):
                if (self.pos[Y]<mousePos[Y] and self.pos[Y]+self.size[Y]>mousePos[Y]):
                    relPos = (mousePos[X]-self.pos[X],mousePos[Y]-self.pos[Y])
                    
                    if(self.img.get_at(relPos)!=self.img.get_colorkey()):
                        return True
        return False
    
    def move(self, change):
        newPos = (self.pos[X]+change[X],self.pos[Y]+change[Y])
        self.pos = newPos
    
    def getPos(self):
        return self.pos
    
    def getImg(self):
        return self.img