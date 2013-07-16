import pygame
from pygame.locals import *
from rypy import *
from actors import *

class Tile2(Drawable):
    def __init__(self,pos=(0,0),img=None):
        super(Tile, self).__init__(pos,img)

class TileMap(list):
    def __init__(self, template, tileSet, tileSize, blankTile='-', iso=False):
        self.tileSize=tileSize
        self.iso = iso
        
        self.actors = dict() #setup dict for actors
        
        for layer in range(0,len(template)):
            self.append(list())
            
            for row in range(0,len(template[layer])):
                self[layer].append(list())
                
                for col in range(0,len(template[layer][row])):
                    if (iso):
                        #get iso tilesize
                        isoSize=(int(tileSize[X]/2),int(tileSize[Y]/2))
                        #get iso position
                        newPos = (col*isoSize[X]+row*int(isoSize[X]),row*isoSize[Y]-row*int(isoSize[Y]/2)-col*int(isoSize[Y]/2))
                    else:
                        #get the standard 2d position
                        newPos = (col*tileSize[X],row*tileSize[Y])
                    
                    #if the tile is an blankTile
                    if (template[layer][row][col]==blankTile):
                        newTile = Tile(newPos) #blank tile
                    else:
                        newImg = tileSet[int(template[layer][row][col])]
                        newTile  = Tile(newPos,newImg)
                    
                    self[layer][row].append(newTile)
                
                #reverse the order of the tiles in each row. doesnt effect position, but
                #fixes issues with iso drawing (iso has to draw from right to left, not L to R)
                #and also with the moving bound points (map verticies), which are reversed for L&R for iso 
                self[layer][row].reverse()
    
    def clearActors(self):
        self.actors.clear()
    
    def delActor(self,name):
        if(self.actors.has_key(name)):
            self.actors[name]=None
    
    def addActors(self,actors):
        for actor in dict(actors).keys():
            self.actors[actor] = actors[actor]
    
    def addActor(self,name,actor):
        self.actors[name]=actor
    
    def move(self,shift,min=None,max=None):
        #get bounds for shifting
        if (min):
            if (self[0][0][0].getPos()[Y]>=min[Y] and shift[Y]>0):
                shift=(shift[X],0)
            if (self[0][0][-1].getPos()[X]>=min[X] and shift[X]>0):
                shift=(0,shift[Y])
            
        if (max):
            if (self[0][-1][-1].getPos()[Y]+self.tileSize[Y]<=max[Y] and shift[Y]<0):
                shift=(shift[X],0)
            if (self[0][-1][0].getPos()[X]+self.tileSize[X]<=max[X] and shift[X]<0):
                shift=(0,shift[Y])
        
        #shift each tile        
        for layer in self:
            for row in layer:
                for tile in row:
                    tile.move(shift)
        
        #shift each actor
        for actor in self.actors.values():
            actor.move(shift)
    
    def draw(self,screen):
        #draw tile layer by layer, row by row, column by column
        for layer in self:
            for row in layer:
                for tile in row:
                    #make sure the tile is visible (in the screen area) before drawing it
                    if (tile.getPos()[X]>=-self.tileSize[X] and tile.getPos()[X]<=screen.get_width()):
                        if (tile.getPos()[Y]>=-self.tileSize[Y] and tile.getPos()[Y]<=screen.get_height()):
                            tile.draw(screen)
        #draw actors
        for actor in self.actors.values():
            #make sure the actor is visible (in the screen area) before drawing it
            if (actor.getPos()[X]>=-self.tileSize[X] and actor.getPos()[X]<=screen.get_width()):
                if (actor.getPos()[Y]>=-self.tileSize[Y] and actor.getPos()[Y]<=screen.get_height()):
                    actor.draw(screen)
    
    def click(self,mousePos):
        topTile = None
        
        for layer in self:
            for row in layer:
                for tile in row:
                    if (tile.click(mousePos)):
                        topTile=tile
                        
        for actor in self.actors.values():
            if(actor.click(mousePos)):
                topTile=actor
        
        return topTile
    
    
class MapTemplate(list):
    def __init__(self,mapFile,dlim='\t'):
        self.mapFile=mapFile
        self.dlim=dlim
        
        self.load()
    
    def load(self):
        readFile = open(self.mapFile,'r')
        
        #setup the first layer
        layer=0
        self.append(list())
        
        for line in readFile:
            #strip out any newline characters
            line = line.rstrip()
            
            if(not line.rstrip().lstrip()):
                layer+=1
                self.append(list())
            else:
                self[layer].append(str(line).split(self.dlim))

class TileSet(list):
    def __init__(self,imgFile,tileSize,transColor=None,offset=(0,0)):
        self.tileSize = tileSize
        self.offset = offset
        self.transColor = transColor
        
        #load tileset image from file
        self.img = loadImage(imgFile,transColor)
        
        self.load()

    def load(self):
        size=self.img.get_size()
        xTiles = int(size[X] / (self.tileSize[X] + self.offset[X]))
        yTiles = int(size[Y] / (self.tileSize[Y] + self.offset[Y]))
        
        for y in range(0,yTiles):
            for x in range (0,xTiles):
                #get the rectangle to steal the tile image from (x,y,width,height)
                tileRect = (x*self.tileSize[X]+x*self.offset[X],
                            y*self.tileSize[Y]+y*self.offset[Y],
                            self.tileSize[X],
                            self.tileSize[Y])
                
                #steal the tile image & add it to the tileset list
                self.append(self.img.subsurface(tileRect))
    