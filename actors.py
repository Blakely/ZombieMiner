import pygame
import re
from rypy import *

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

class testSprite(Drawable):
    def __init__(self,pos,spriteset,fps):
        self.dir = 0
        self.act = 0
        self.frame = 0
        self.spriteset = spriteset
        super(testSprite, self).__init__(pos,spriteset[self.act][self.dir][self.frame])
        
        self.delay = 1000 / fps
        self.last = pygame.time.get_ticks()
        
    def animate(self, elapsed):
        if (elapsed - self.last > self.delay):
            self.frame += 1
            if self.frame >= len(self.spriteset[self.act][self.dir]):
                self.frame = 0
            self.img = self.spriteset[self.act][self.dir][self.frame]
            self.last=elapsed
            return True
        return False     
    
    def update(self):
        self.animate(pygame.time.get_ticks())
        #if (self.act==1):
         #   if (self.frame!=len(spriteset[self.act][self.dir])):
          #      self.animate(pygame.time.get_ticks())
           #     self.move(self.dist)
            #else:
             #   self.animate(pygame.time.get_ticks())
              #  self.act=0
            
    
    def setDir(self,_dir):
        if(self.act==0 and self.dir!=_dir):
            self.dir=_dir


class Actor(Drawable):
    def __init__(self,pos,spriteset,fps):
        self.dir = 0
        self.act = 0
        self.frame = 0
        self.spriteset = spriteset
        super(Actor, self).__init__(pos,spriteset[self.act][self.dir][self.frame])
        
        self.delay = 1000 / fps
        self.last = pygame.time.get_ticks()
        
    def animate(self, elapsed):
        if(self.act>=0):
            if (elapsed - self.last > self.delay):
                self.frame += 1
                if self.frame >= len(self.spriteset[self.act][self.dir]):
                    self.frame = 0 
                self.img = self.spriteset[self.act][self.dir][self.frame]
                self.last=elapsed
                return True
        return False     
    
    def update(self):
        if (self.act==1):
            if (self.animate(pygame.time.get_ticks())):
                self.move(self.stepDist)
                if(self.frame==0):
                    self.act=0
                    self.move(self.extraDist)
                    self.last+=3000
            
    
    def setDir(self,_dir):
        if(self.act==0 and self.dir!=_dir):
            self.dir=_dir
    
    def walk(self,dist):
        if(self.act==0):
            self.act=1
            numFrames = len(self.spriteset[self.act][self.dir])
            self.extraDist=(dist[X]%numFrames,dist[Y]%numFrames)
            self.stepDist = (dist[X]/numFrames,dist[Y]/numFrames)

    def getImg(self):
        return self.spriteset.getImg()
    
class SpriteSet(list):
    def __init__(self,setImg,frameSize,setTemplate):
        self.setImg=setImg
        self.frameSize = frameSize
        
        for act in range(0,len(setTemplate)):
            self.append(list())
            
            for direction in range(0,len(setTemplate[act])):
                self[act].append(list())
                
                for frame in range(0,len(setTemplate[act][direction])):
                    frameNum = int(re.sub(r'[^\d]+','0',setTemplate[act][direction][frame]))
                    frameRect = (frameNum*frameSize[X],
                                 0,
                                 frameSize[X],
                                 frameSize[Y])
                    frameImg = setImg.subsurface(frameRect)
                    
                    if ("^" in setTemplate[act][direction][frame]):
                        frameImg = pygame.transform.flip(frameImg,True,False)
                    
                    self[act][direction].append(frameImg)
                    
    def getImg(self):
        return self.setImg
    
    def getFrameSize(self):
        return self.frameSize
            

class SpriteSheet(list):
    def __init__(self,template):
        #get the necessary parameters
        self.tileSize = (int(template["tilesize"][X]),int(template["tilesize"][Y]))
        
        transColor = Color(template["trans"][0],template["trans"][1],template["trans"][2])
        self.img = loadImage(template["file"],transColor)
        
        self.load()

    def load(self):
        size=img.get_size()
        yTiles = int(size[Y] / self.tileSize[Y])
        
        for y in range(0,yTiles):
            #get the rectangle to steal the spriteset image from (x,y,width,height)
            setRect = (0,
                       y*self.tileSize[Y],
                       size[X],
                       self.tileSize[Y])
            
            setTemp = (template["still"],template["move"],template["atk"])
            self.append(SpriteSet(self.img.subsurface(setRect)))


class SpriteSheetTemplates(list):
    def __init__(self,templateFile,pdlim,vdlim,lstdlim,flip=None):
        self.templateFile
        self.dlim=dlim
        
        self.load()
    
    def load(self):
        readFile = open(self.templateFile,'r')
        
        self.append(dict())
        ss = 0
        
        for line in readFile:
            #strip out any extra whitespace
            line = line.rstrip()
            
            #if its a blank line, get ready for the next spritesheet template
            if(not line):
                ss+=1
                self.append(dict())
            
            #if there is data on the line, parse it
            else:
                prop=str(line).split(pdlim) #split property name from value
                prop[0]=prop[0].rstrip()
                
                self[ss][prop[0]]=list()
                
                #if the properties value contains the value delimiter, make a list of it
                if(vdlim in prop[1]):
                    currVal=0
                    #loop through each value in the value-list (split by the value-delimiter)
                    for val in str(prop[1]).split(vdlim):
                        
                        #if the value contains the list dlimiter
                        if(lstdlim in val):
                            #parse the list from the value and save it
                            valLst = str(val).split(lstdlim)
                            self[ss][prop[0]][currVal]=valLst
                        
                        else: #otherwise, append the value to the properties value-list
                            self[ss][prop[0]].append(val)
                            
                        currVal+=1
                
                else: #otherwise, simply set the value to the property 
                    self[ss][prop[0]].append(prop[1])   
                
class SpriteSheetList(dict):
    def __init__(self,templates):
        #loop through each template
        for template in templates:
            #create a spritesheet for each template and append it to the list
            self[template["name"]]=SpriteSheet(template)
    
    #def getSpriteSet(self,ssName,)
    #    return self[ssName].getSpriteSet##
                