#import needed modules for pygame
import pygame, sys
from pygame.locals import *
import math

#import needed classes for tile based game
from tiles import *
from actors import *

import random

TILE_TRANSCOLOR = Color(255,0,255)
TILE_HIGHLIGHT = 80 #percentage to dim selection to on highlight

DIR_RIGHT=0
DIR_LEFT=1
DIR_UP=2
DIR_DOWN=3

MINE_DUG = 21

MINE_BLOCK_FULL=2
MINE_BLOCK_UP=1
MINE_BLOCK_NONE = 0

mines={ 0:{'chance':18,'value':0,'block':MINE_BLOCK_FULL},
        1:{'chance':80,'value':1,'block':MINE_BLOCK_NONE,'hits':4},
        2:{'chance':22,'value':1,'block':MINE_BLOCK_NONE,'hits':5},
        3:{'chance':17,'value':1,'block':MINE_BLOCK_NONE,'hits':7},
        4:{'chance':15,'value':1,'block':MINE_BLOCK_NONE,'hits':8},
        5:{'chance':14,'value':1,'block':MINE_BLOCK_NONE,'hits':10},
        6:{'chance':12,'value':1,'block':MINE_BLOCK_NONE,'hits':12},
        7:{'chance':10,'value':1,'block':MINE_BLOCK_NONE,'hits':15},
        8:{'chance':9,'value':1,'block':MINE_BLOCK_NONE,'hits':17},
        9:{'chance':8,'value':1,'block':MINE_BLOCK_NONE,'hits':20},
        10:{'chance':7,'value':1,'block':MINE_BLOCK_NONE,'hits':23},
        11:{'chance':6,'value':1,'block':MINE_BLOCK_NONE,'hits':26},
        12:{'chance':5,'value':1,'block':MINE_BLOCK_NONE,'hits':30},
        13:{'chance':4,'value':1,'block':MINE_BLOCK_NONE,'hits':32},
        14:{'chance':3,'value':1,'block':MINE_BLOCK_NONE,'hits':34},
        15:{'chance':2,'value':1,'block':MINE_BLOCK_NONE,'hits':35},
        16:{'chance':1,'value':1,'block':MINE_BLOCK_NONE,'hits':40},
        17:{'chance':0,'value':1,'block':MINE_BLOCK_NONE,'hits':80},
        18:{'chance':0,'value':0,'block':MINE_BLOCK_UP,},
        19:{'chance':0,'value':0,'block':MINE_BLOCK_FULL},
        20:{'chance':0,'value':0,'block':MINE_BLOCK_FULL},
        21:{'chance':0,'value':0,'block':MINE_BLOCK_NONE}
      }

#initialize pygame
pygame.init()

#draws the game screen
# screen - the pygame screen being drawn to
# state - int representing the games current state
# reels - a list representing the spun reels
# texts - tuple of form (bet, pot, cash, msg), representing current game values
def drawGame(screen,buttons=None):
    #clear the screen & redraw bg
    #screen.fill(COLOR_BLACK)
    
    
    #update the display
    pygame.display.flip()
          

                
#=========================================================================================
#                     MAIN/GAME FUNCTIONS
#=========================================================================================

#Generic graphical object              
class Drawable(object):
    def __init__(self, pos=(0,0),img=None,maskSet=None):
        self.pos = pos
        
        if(img):
            #create a copy, so it can be modified if necessary and not affect other drawables using the same image
            self.img = img.copy() 
            self.size = img.get_size()
        else:
            self.img=None
            
        self.maskSet = maskSet #does not make copies of the maskimages-must be handled at a higher level if you want to modify them
        self.maskImg = None #init current maskimage
        
    def draw(self,screen,offsetPos=(0,0)):
        #draw the image if theres something to draw, and similar for the maskimage
        if(self.img):
            screen.blit(self.img,(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y]))
        if(self.maskImg):
            screen.blit(self.maskImg,(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y]))
    
    def move(self, change):
        newPos = (self.pos[X]+change[X],self.pos[Y]+change[Y])
        self.pos = newPos
    
    def getPos(self):
        return self.pos
    
    def getImg(self):
        return self.img

class Tile(Drawable):
    def __init__(self,attributes,pos=(0,0),img=None,maskFrames=None):
        self.setAttributes(attributes)
        
        #if the tile can be hit, init its HP
        if (self.attributes.has_key('hits')):
            self.attributes['hp']=self.attributes['hits']
        
        super(Tile, self).__init__(pos,img,maskFrames)
    
    def setAttributes(self,attributes):
        #make a copy of the attributes so they can be modifed and not affect other tiles using the same ones
        self.attributes = attributes.copy()
    
    def getAttributes(self):
        return self.attributes
    
    def hit(self):
        #if the tile has hp, hit it!
        if (self.attributes.has_key('hp')):
            self.attributes['hp']-=1
            
            #if hp hits 0, reset the mask and return its value
            if(self.attributes['hp']==0):
                self.maskImg=None
                return self.attributes['value']
            
            #if there are mask imgs, determine which mask img to use based on the state of the hp & number of mask frames
            if(self.maskSet):
                #small note - cast hits to float to force float division in py2.7
                #this is safe since hits/hp>=1 (always) and the top numerator is maskframes, so maskstate!>len(maskimgs)
                maskState=int(len(self.maskSet)/(float(self.attributes['hits'])/self.attributes['hp']))
                              
                self.maskImg=self.maskSet[-maskState-1]
        
        return None
            
                
class Miner(Drawable):
    def __init__(self,pos,spriteset,stats):
        self.dir = 0
        self.act = 0
        self.frame = 0
        self.spriteset = spriteset
        self.stats = stats
        
        #get the absolute position of the miner (framesize*given pos)
        absPos = (pos[X]*spriteset.getFrameSize()[X],pos[Y]*spriteset.getFrameSize()[Y])
        super(Miner, self).__init__(absPos,spriteset[self.act][self.dir][self.frame])
        
        self.frameDelay = 100 / self.stats["sp"]
        self.actDelay = 50 / self.stats["sp"]
        self.lastMod = pygame.time.get_ticks()
        
    def animate(self, elapsed, delay):     
        if(self.act>=0):
            if (elapsed - self.lastMod > delay):
                self.frame += 1
                if self.frame >= len(self.spriteset[self.act][self.dir]):
                    self.frame = 0 
                self.img = self.spriteset[self.act][self.dir][self.frame]
                self.lastMod=elapsed
                return True
        return False     
    
    def update(self):
        returnAct = self.act
        
        #exceptional delay cases for when the player is falling
        if(self.act==3):
            fdelay=200
            adelay=0
        else:
            fdelay=self.frameDelay
            adelay=self.actDelay
        
        if (self.act>0):
            if (self.animate(pygame.time.get_ticks(),fdelay)):
                self.move(self.stepDist)
                
                #if the action is complete (all frames been played)
                if(self.frame==0):
                    self.lastMod+=adelay #delay the next action by adelay milliseconds
                    
                    #reset for next act
                    self.act=0
                    self.stepDist=0
                    
                    return returnAct;
                
                #if we moved but didn't complete the act return the distance tuple
                if(self.stepDist!=(0,0)):
                    return (self.stepDist)
        
        return None
    
    def setDir(self,_dir):
        if(self.act==0 and self.dir!=_dir):
            self.dir=_dir
            self.img = self.spriteset[self.act][self.dir][self.frame]
    
    def doAction(self,action,dist=(0,0)):
        if(self.act==0):
            self.act=action
            numFrames = len(self.spriteset[self.act][self.dir])
            #self.extraDist=(dist[X]%numFrames,dist[Y]%numFrames)
            self.stepDist = (dist[X]/numFrames,dist[Y]/numFrames)
            return True
        return False
    
    def getImg(self):
        return self.spriteset.getImg()
    
    def getPos(self):
        return (self.pos[X]/self.spriteset.getFrameSize()[X],self.pos[Y]/self.spriteset.getFrameSize()[Y])


class MineMap(list):
    def __init__(self, template, tileSet, tileSize, player=None,tileMaskSet=None):
        self.tileSize=tileSize
        self.player = player
        
        self.shift=(0,0)
        
        #loop through each row in the template
        for row in range(0,len(template)):
            #create a list to hold that row
            self.append(list())
            
            #loop through each column (of each row) in the template
            for col in range(0,len(template[row])):
                #get the position and img of the tile in that row+column
                newPos = (col*tileSize[X],row*tileSize[Y])
                newImg = tileSet[int(template[row][col])]
                
                #create a new tile and add it to the minemap
                newTile  = Tile(mines[int(template[row][col])],newPos,newImg,tileMaskSet)
                self[row].append(newTile)

    
    def swapPlayer(self,name,player):
        self.player=player
    
    def move(self,shift,min=None,max=None):
        #get bounds for shifting
        if (min): #minumum bound 
            if (self[0][0].getPos()[Y]+self.shift[Y]>=min[Y] and shift[Y]>0):
                shift=(shift[X],0)
            if (self[0][0].getPos()[X]+self.shift[X]>=min[X] and shift[X]>0):
                shift=(0,shift[Y])
                
        if (max): #maximum bound
            if (self[-1][-1].getPos()[Y]+self.shift[Y]+self.tileSize[Y]<=max[Y] and shift[Y]<0):
                shift=(shift[X],0)
            if (self[-1][-1].getPos()[X]+self.shift[X]+self.tileSize[X]<=max[X] and shift[X]<0):
                shift=(0,shift[Y])
        self.shift = (self.shift[X]+shift[X],self.shift[Y]+shift[Y])
        
    def draw(self,screen):
        #draw tile row by row, column by column
        for row in self:
            for tile in row:
                #make sure the tile is visible (in the screen area) before drawing it
                if (tile.getPos()[X]+self.shift[X]>=-self.tileSize[X] and tile.getPos()[X]+self.shift[X]<=screen.get_width()):
                    if (tile.getPos()[Y]+self.shift[Y]>=-self.tileSize[Y] and tile.getPos()[Y]+self.shift[Y]<=screen.get_height()):
                        tile.draw(screen,self.shift)

        #make sure the player is visible (in the screen area) before drawing it
        if (self.player.getPos()[X]>=-self.tileSize[X] and self.player.getPos()[X]<=screen.get_width()):
            if (self.player.getPos()[Y]>=-self.tileSize[Y] and self.player.getPos()[Y]<=screen.get_height()):
                #draw the player
                self.player.draw(screen,self.shift)
    
    def getTile(self,pos):
        return self[pos[Y]][pos[X]]
    
    def getTileSize(self):
        return self.tileSize
    
    def getAbsSize(self):
        return (len(self[0])*self.tileSize[X],len(self)*self.tileSize[Y])
    
    def getSize(self):
        return (len(self[0]),len(self))


class mapReader(list):
    def __init__(self,mapFile,dlim='\t'):
        self.mapFile=mapFile
        self.dlim=dlim
        
        self.load()
    
    def load(self):
        readFile = open(self.mapFile,'r')
        
        for line in readFile:
            #strip out any newline characters
            line = line.rstrip()
            self.append(str(line).split(self.dlim))


class randomMapTemplate2(list):
    def __init__(self,size,tileTemplates):
        self.size=size
        
        #for weighted random item selection algorithm
        chanceSum = 0;
        for cs in tileTemplates.keys():
            chanceSum+=tileTemplates[cs]['chance']
        
        for row in range(0,self.size[Y]):
            self.append(list())
            
            for col in range(0,self.size[X]):
                rnd = random.randint(0,chanceSum)
                lowest=0
        
                for c in tileTemplates.keys():
                    chance = tileTemplates[c]['chance']
                    if(rnd<chance):
                        self[row].append(c)
                        break
                    rnd-=chance

    
    def setBorder(self,borderVal):
        for top in range(0,len(self[0])):
            self[0][top]=borderVal
        
        for bottom in range(0,len(self[-1])):
            self[-1][bottom]=borderVal
            
        for row in self:
            row[0]=borderVal
            row[-1]=borderVal
           
        
    def setArea(self,startPos,template):
        for row in range(0,len(template)):
            for col in range(0,len(template[row])):
                self[row+startPos[Y]][col+startPos[X]]=template[row][col]


class randomMapTemplate(list):
    def __init__(self,size,rnge):
        self.size=size
        self.range = rnge
        
        
        for row in range(0,self.size[Y]):
            self.append(list())
            
            for col in range(0,self.size[X]):
                randTile = random.randint(0,rnge)
                self[row].append(randTile)
    
    def setBorder(self,borderVal):
        for top in range(0,len(self[0])):
            self[0][top]=borderVal
        
        for bottom in range(0,len(self[-1])):
            self[-1][bottom]=borderVal
            
        for row in self:
            row[0]=borderVal
            row[-1]=borderVal
           
        
    def setArea(self,startPos,template):
        for row in range(0,len(template)):
            for col in range(0,len(template[row])):
                self[row+startPos[Y]][col+startPos[X]]=template[row][col]



def tryAction(screen,player,direction,tilemap):
    if(direction==DIR_RIGHT):
        move=(1,0)
    elif(direction==DIR_LEFT):
        move=(-1,0)
    elif(direction==DIR_UP):
        move=(0,-1)
    elif(direction==DIR_DOWN):
        move=(0,1)
        
    nextPos = (player.getPos()[X]+move[X],player.getPos()[Y]+move[Y])
    
    if(nextPos[X]>=0 and nextPos[X]<=tilemap.getSize()[X] and
       nextPos[Y]>=0 and nextPos[Y]<=tilemap.getSize()[Y]):
        nextTile = tilemap.getTile(nextPos)
    
  #      if(nextTile.getAttributes()['block']==MINE_BLOCK_FULL):
   #         pass
    #    elif (direction==DIR_UP and tilemap.getTile(player.getPos()).attributes['block']==MINE_BLOCK_UP):
     #       pass
      #  elif (nextTile.getAttributes()['value']>0):
       #     if(player.doAction(2)):
        #        return nextTile
        #else:
        if(player.doAction(1,(move[X]*tilemap.getTileSize()[X],move[Y]*tilemap.getTileSize()[Y]))):
            return nextTile

def scrollMap(screen,player,tilemap,moveVect):
    print player.getPos()[X]
    print moveVect
    if (player.getPos()[X]<3 or player.getPos()[X]>tilemap.getSize()[X]-3 or player.getPos()[X]==3 and player.dir==DIR_RIGHT):
        moveVect=(0,moveVect[Y])
    if (player.getPos()[Y]<4 or player.getPos()[X]>=tilemap.getSize()[Y]-4):
        moveVect=(moveVect[X],0)
    
    print moveVect
    tilemap.move((-moveVect[X],-moveVect[Y]),(0,0),screen.get_size())
               
#main game loop - runs until the user quits
# screen - 
def game(screen):
    #load the spriteset image for the player (miner)
    spriteImg=loadImage('miner4.png',Color(255,0,255))
    #setup the spriteset template (RL)
    spriteTemplate=[[['0'],['^0']], #standing
                    [['0','1','2','3'],['^0','^1','^2','^3']], #walking
                    [['4','5','6','7'],['^4','^5','^6','^7']], #axing
                    [['1','3'],['^1','^3']]] #falling
    #setup player stats and create the player
    stats = {'sp':1,'str':1}
    player = Miner((3,4),SpriteSet(spriteImg,(48,48),spriteTemplate),stats)
    
    
    #create the template for the mine map
    template=randomMapTemplate2((50,50),mines) #create random map template of mines
    template.setBorder(0) #set the border to be all unbreakable bricks
    aboveground=mapReader('above.txt','\t') #load in custom map for aboveground
    template.setArea((0,0),aboveground) #combine random minemap with aboveground map @ top left corner

        
    #load in the tileset and tile maskset for the game 
    tileset = TileSet('mines.png',(48,48),TILE_TRANSCOLOR)
    maskSet = TileSet('cracks.png',(48,48),TILE_TRANSCOLOR)
    
    #create the MineMap (tilemap for the game)
    tilemap=MineMap(template,tileset,(48,48),player,maskSet)
    
    #set pygame to "repeat" key-presses (basically key toggling)
    pygame.key.set_repeat(50,50)
    
    actResult=None
    
    #begin game loop
    while True:
        
        #check all of the events that have occured since last loop
        for event in pygame.event.get():
            #if users quits, exit the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if (event.key==K_UP):
                    direction = DIR_UP

                elif (event.key==K_DOWN):
                    direction = DIR_DOWN

                elif (event.key==K_LEFT):
                    direction = DIR_LEFT
                    player.setDir(DIR_LEFT)
                    
                elif (event.key==K_RIGHT):
                    direction = DIR_RIGHT
                    player.setDir(DIR_RIGHT)
                    
                tryResult=tryAction(screen,player,direction,tilemap)
                if(tryResult):
                    actResult=tryResult
            elif event.type == MOUSEBUTTONDOWN:
                pass #FIX - buttons?

        finishedAct=player.update()
        
        #if the finished act is a tuple
        if (type(finishedAct) is tuple):
            moveVect = finishedAct
            #scroll the map the distance that the player has moved
            scrollMap(screen,player,tilemap,moveVect)
        
        #done walking
        if (finishedAct==1):
            #finish scrolling the distance the player has moved
            scrollMap(screen,player,tilemap,moveVect)
            print ""
            
        #done hitting
        elif (finishedAct==2):
            hitTile = actResult
            hitResult = hitTile.hit()
            
            #if the hit returned a result (broke?)
            if(hitResult):
                #set the dug-out tiles attributes and image
                hitTile.setAttributes(mines[MINE_DUG]);
                hitTile.img = tileset[MINE_DUG]
        
        #clear the screen and redraw the tilemap, then update the display
        screen.fill(Color(0,0,0))
        tilemap.draw(screen)
        pygame.display.flip()
    
    
#main program - sets up pygame & starts game
def main():
    #setup game screen
    gameScreen = pygame.display.set_mode((400,450))
    
    #start the game
    game(gameScreen);

#Start program
if __name__ == "__main__":
    main()