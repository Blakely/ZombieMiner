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

IMG_ZOMBIE='zombie.png'
IMG_PLAYER='player.png'
IMG_CRACKS='cracks.png'
IMG_TILESET='mines.png'
IMG_FIRE='fire.png'

ZOMBIE_NUM=10
ZOMBIE_STR=0.1
ZOMBIE_SP=0.1

MINE_DUG = 21
MINE_ROCK=0

MINE_BLOCK_FULL=2
MINE_BLOCK_UP=1
MINE_BLOCK_NONE = 0

MINE_VAL_WIN=-1

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
        17:{'chance':0,'value':MINE_VAL_WIN,'block':MINE_BLOCK_NONE,'hits':80},
        18:{'chance':0,'value':0,'block':MINE_BLOCK_UP,},
        19:{'chance':0,'value':0,'block':MINE_BLOCK_FULL},
        20:{'chance':0,'value':0,'block':MINE_BLOCK_FULL},
        21:{'chance':0,'value':0,'block':MINE_BLOCK_NONE}
      }

AI_CHECKORDER = {DIR_UP:    [DIR_UP,DIR_RIGHT,DIR_LEFT,DIR_DOWN],
                 DIR_RIGHT: [DIR_RIGHT,DIR_UP,DIR_DOWN,DIR_LEFT],
                 DIR_LEFT:  [DIR_LEFT,DIR_UP,DIR_DOWN,DIR_RIGHT],
                 DIR_DOWN:  [DIR_DOWN,DIR_RIGHT,DIR_LEFT,DIR_UP]}

#initialize pygame
pygame.init()

                
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
    
    def change(self,newAtt,newImg):
        self.setAttributes(newAtt)
        self.img = newImg
    
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
        #setup basic state variables
        self.dir = 0
        self.act = 0
        self.frame = 0
        self.maskFrame=0
        self.spriteset = spriteset
        self.stats = stats
        
        #get the absolute position of the miner (framesize*given pos)
        absPos = (pos[X]*spriteset.getFrameSize()[X],pos[Y]*spriteset.getFrameSize()[Y])
        super(Miner, self).__init__(absPos,spriteset[self.act][self.dir][self.frame])
        
        #setup antimation-related variables
        self.frameDelay = 100 / self.stats["sp"]
        self.actDelay = 50 / self.stats["sp"]
        self.lastMod = pygame.time.get_ticks()
        self.maskMod = pygame.time.get_ticks()
        
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
    
    def animateMask(self,elapsed,delay):
        if (elapsed - self.maskMod > delay):
            self.maskFrame += 1
            if self.maskFrame >= len(self.maskSet):
                self.maskFrame = 0
                return True
            self.maskImg = self.maskSet[self.maskFrame]
            self.maskMod=elapsed
        return False     
    
    def updateMask(self,maskSet,frameDelay):
        #if this is a new maskSet, store it
        if(self.maskSet!=maskSet):
            self.maskSet=maskSet
        
        #try to animate the mask - when its done, return success   
        if (self.animateMask(pygame.time.get_ticks(),frameDelay)):
            self.maskImg=None
            return True
        
        return False
    
    def setDir(self,_dir):
        if(self.act==0 and self.dir!=_dir):
            self.dir=_dir
            self.img = self.spriteset[self.act][self.dir][self.frame]
    
    def doAction(self,action,dist=(0,0)):
        if(self.act==0):
            self.act=action
            numFrames = len(self.spriteset[self.act][self.dir])
            self.stepDist = (dist[X]/numFrames,dist[Y]/numFrames)
            return True
        return False
    
    def getImg(self):
        return self.spriteset.getImg()
    
    def getPos(self):
        return (self.pos[X]/self.spriteset.getFrameSize()[X],self.pos[Y]/self.spriteset.getFrameSize()[Y])


class AI(object):
    def __init__(self,target):
        self.target=target
    
    def chooseDir(self,myPos,nearTiles):
        #if there are "near tiles" (FIX - for bug)
        if(nearTiles):
            targetPos=self.target.pos
            chkOrder=list()
            if(myPos[Y]>targetPos[Y]):
                chkOrder = AI_CHECKORDER[DIR_UP]
            elif(myPos[X]<targetPos[X]):
                chkOrder = AI_CHECKORDER[DIR_RIGHT]
            elif(myPos[Y]<targetPos[Y]):
                chkOrder = AI_CHECKORDER[DIR_DOWN]
            elif(myPos[X]>targetPos[X]):
                chkOrder = AI_CHECKORDER[DIR_LEFT]
                
            for direction in chkOrder:
                if(nearTiles[direction].attributes['block']!=MINE_BLOCK_FULL):
                    return direction
            
        return DIR_LEFT #default to trying to go left - doesn't matter, AI cant move
                   

class Mob(Miner):
    def __init__(self,pos,spriteset,stats,ai):
        self.ai=ai
        super(Mob, self).__init__(pos,spriteset,stats)
        
    def runAI(self,nearTiles):
        newDir = self.ai.chooseDir(self.pos,nearTiles)
        
        if(newDir==DIR_RIGHT or newDir==DIR_LEFT):
            self.setDir(newDir)
            
        return newDir
    
    def dying(self,deathSet,frameDelay):
        return self.updateMask(deathSet,frameDelay)
        


class MineMap(list):
    def __init__(self, template, tileSet, tileSize, player=None,tileMaskSet=None):
        self.tileSize=tileSize
        self.player = player
        
        self.shift=(0,0) #init the maps "shift" (how much its been scrolled)
        
        self.mobs = list() #init list for mobs
        
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
    
    def clearMob(self,mobIndex):
        self.mobs.pop(mobIndex)
    
    def addMobs(self,mobs):
        for mob in mobs:
            self.mobs.append(mob)
    
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
        
        #loop through and draw each mob
        for mob in self.mobs:
            #make sure mob is visible (in screen area) before drawing it
            if (mob and mob.getPos()[X]>=-self.tileSize[X] and mob.getPos()[X]<=screen.get_width()):
                if (mob.getPos()[Y]>=-self.tileSize[Y] and mob.getPos()[Y]<=screen.get_height()):
                    #draw the mob
                    mob.draw(screen,self.shift)
    
    
    def getTile(self,pos):
        return self[pos[Y]][pos[X]]
    
    def getTileSize(self):
        return self.tileSize
    
    def getAbsSize(self):
        return (len(self[0])*self.tileSize[X],len(self)*self.tileSize[Y])
    
    def getSize(self):
        return (len(self[0]),len(self))
    
    def getNearTiles(self,pos):
        #FIX - unknown bug here that i cant consistently reproduce. just return null if it arises
        try:
            #in order of R L U D
            return [self[pos[Y]][pos[X]+1],self[pos[Y]][pos[X]-1],self[pos[Y]-1][pos[X]],self[pos[Y]+1][pos[X]]]
        except IndexError:
            return None


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


class randomMapTemplate(list):
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


def tryAction(screen,miner,direction,tilemap):
    if(direction==DIR_RIGHT):
        move=(1,0)
    elif(direction==DIR_LEFT):
        move=(-1,0)
    elif(direction==DIR_UP):
        move=(0,-1)
    elif(direction==DIR_DOWN):
        move=(0,1)
        
    nextPos = (miner.getPos()[X]+move[X],miner.getPos()[Y]+move[Y])
    
    if(nextPos[X]>=0 and nextPos[X]<=tilemap.getSize()[X] and
       nextPos[Y]>=0 and nextPos[Y]<=tilemap.getSize()[Y]):
        nextTile = tilemap.getTile(nextPos)
    
        if(nextTile.getAttributes()['block']==MINE_BLOCK_FULL):
            pass
        elif (direction==DIR_UP and tilemap.getTile(miner.getPos()).attributes['block']==MINE_BLOCK_UP):
            pass
        elif (nextTile.getAttributes()['value']>0):
            if(miner.doAction(2)):
                return nextTile
        else:
            if(miner.doAction(1,(move[X]*tilemap.getTileSize()[X],move[Y]*tilemap.getTileSize()[Y]))):
                return nextTile


def scrollMap(screen,player,tilemap,moveVect):
    if (player.getPos()[X]<3 or player.getPos()[X]>tilemap.getSize()[X]-3 or player.getPos()[X]==3 and player.dir==DIR_RIGHT):
        moveVect=(0,moveVect[Y])
    if (player.getPos()[Y]<4 or player.getPos()[X]>=tilemap.getSize()[Y]-4):
        moveVect=(moveVect[X],0)
    
    tilemap.move((-moveVect[X],-moveVect[Y]),(0,0),screen.get_size())


def createZombies(tilemap,tileset,spriteTemplate,player,startPos=(0,0)):
    zombieImg=loadImage(IMG_ZOMBIE,TILE_TRANSCOLOR) #load spriteset image for zombies
    zombieAI = AI(player) #setup a simple AI that targets the player
    
    zombies=list() #holder list for zombies
    
    #create ZOMBIE_NUM # of zombies
    for z in range(0,ZOMBIE_NUM):
        #randomly choose a position for the zombie to start -- goes to width -1 and height - 1, to account for border
        randomPos = (random.randint(startPos[X],tilemap.getSize()[X]-2),random.randint(startPos[Y],tilemap.getSize()[Y]-2))
        #base stats on the random position - further down zombies will be harder/faster
        zombieStats = {'sp':ZOMBIE_SP*(randomPos[X]+randomPos[Y])/2,'str':ZOMBIE_STR*(randomPos[X]+randomPos[Y])/2}
        
        zombie = Mob(randomPos,SpriteSet(zombieImg,(48,48),spriteTemplate),zombieStats,zombieAI)
        zombies.append(zombie)
        
        #change the tile to be a "broken" one at the randomly chose position
        tilemap.getTile(randomPos).change(mines[MINE_DUG],tileset[MINE_DUG])
    
    return zombies

#main game loop - runs until the user quits
# screen - 
def game(screen):
    #load the spriteset image for the player (miner)
    playerImg=loadImage(IMG_PLAYER,TILE_TRANSCOLOR)
    
    #setup the spriteset template (RL) for both player and zombie
    spriteTemplate=[[['0'],['^0']], #standing
                    [['0','1','2','3'],['^0','^1','^2','^3']], #walking
                    [['4','5','6','7'],['^4','^5','^6','^7']], #axing
                    [['1','3'],['^1','^3']]] #falling
    
    #setup and create the player
    playerStats = {'sp':1,'str':1}
    player = Miner((3,4),SpriteSet(playerImg,(48,48),spriteTemplate),playerStats)
    
    #create the template for the mine map
    template=randomMapTemplate((50,50),mines) #create random map template of mines
    template.setBorder(MINE_ROCK) #set the border to be all unbreakable bricks
    aboveground=mapReader('above.txt','\t') #load in custom map for aboveground
    template.setArea((0,0),aboveground) #combine random minemap with aboveground map @ top left corner

        
    #load in the tileset and tile maskset for the game 
    tileset = TileSet(IMG_TILESET,(48,48),TILE_TRANSCOLOR)
    maskSet = TileSet(IMG_CRACKS,(48,48),TILE_TRANSCOLOR)
    
    #create the MineMap (tilemap for the game) and create/add zombies
    tilemap=MineMap(template,tileset,(48,48),player,maskSet)
    zombies=createZombies(tilemap,tileset,spriteTemplate,player,(1,len(aboveground))) 
    tilemap.addMobs(zombies)
    
    #setup the fire spriteset for any zombies that need to burn!
    fireImg=loadImage(IMG_FIRE,TILE_TRANSCOLOR)
    fireTemplate=[[['0','1','2','^1','3','^2','0','3','2']]] #uses a template/spriteset so it can have duplicates of frames 
    fireSet=SpriteSet(fireImg,(48,48),fireTemplate)[0][0] #spritesets are dicts, but we only need the first "act"+"dir" of it for this
    
    #set pygame to "repeat" key-presses (basically key toggling)
    pygame.key.set_repeat(50,50)
    
    pActTile=None
    zActTile=None
    
    #begin game loop
    while True:
        
        #check all of the events that have occured since last loop
        for event in pygame.event.get():
            #if users quits, exit the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            #if a key was pressed    
            elif event.type == KEYDOWN:
                #determine which direction to act based on what key was pressed
                if (event.key==K_UP):
                    direction = DIR_UP

                elif (event.key==K_DOWN):
                    direction = DIR_DOWN

                elif (event.key==K_LEFT):
                    direction = DIR_LEFT
                    player.setDir(DIR_LEFT) #change the visual direction of the player sprite
                    
                elif (event.key==K_RIGHT):
                    direction = DIR_RIGHT
                    player.setDir(DIR_RIGHT) #change the visual direction of the player sprite
                    
                #try to act on the next tile in the chosen direction
                pTryResult=tryAction(screen,player,direction,tilemap)
                if(pTryResult): #if the action went through, get which tile was affect
                    pActTile=pTryResult
                    
            elif event.type == MOUSEBUTTONDOWN:
                pass #FIX - buttons?

        #update the player and get the returned action data
        playerAct=player.update()
        
        #if the finished act is a tuple
        if (type(playerAct) is tuple):
            moveVect = playerAct
            #scroll the map the distance that the player has moved
            scrollMap(screen,player,tilemap,moveVect)
        #done walking
        elif (playerAct==1):
            #finish scrolling the distance the player has moved
            scrollMap(screen,player,tilemap,moveVect)
        #done hitting
        elif (playerAct==2):
            pHitTile = pActTile
            pHitResult = pHitTile.hit()
            
            #if the hit returned a result (broke?)
            if(pHitResult):
                #set the dug-out tiles attributes and image to "dug" tile
                pHitTile.change(mines[MINE_DUG],tileset[MINE_DUG])
        
        for z in range(0,len(zombies)):
            zombie=zombies[z]
            
            #if the zombie is outside...
            if (tilemap.getTile(zombie.getPos()).attributes['block']==MINE_BLOCK_UP):
                if(zombie.dying(fireSet,200)):
                    tilemap.clearMob(z)
                    zombies.remove(zombie)
                    break
            
            #let the AI kick in to choose a direction,then try and act in that direction
           
            nearTiles=tilemap.getNearTiles(zombie.getPos()) #get tiles around zombie
            newDir=zombie.runAI(nearTiles)#get ai to choose path
            
            #try to act in the direction chosen
            zTryResult = tryAction(screen,zombie,newDir,tilemap)
            if(zTryResult):
                zActTile=zTryResult
                    
            #update the zombie and get the returned action data
            zombieAct=zombie.update()
            
            #if the zombie is hitting
            if (zombieAct==2):
                zHitTile = zActTile #get the tile the zombie is trying to hit
                zHitResult = zHitTile.hit()
                
                #if the hit returned a result (broke?)
                if(zHitResult):
                    #set the dug-out tiles attributes and image to "dug" tile
                    zHitTile.change(mines[MINE_DUG],tileset[MINE_DUG]);
        
        
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