#Filename: gameObjects.py
#Author: Ryan Blakely
#Last Modified By: Ryan Blakely
#Last Modified: July 15th, 2013
#Description: Objects required for the ZombieMiner.py game


import pygame,math,random,re
from pygame.locals import *

from gameConstants import *
from gameFunctions import *


#A Generic Drawable object
#pos (tuple) - the absolute position of the drawable on the screen
#img (pygame Surface) - the image to draw for the drawable
#maskSet (list) - the image set for a mask
class Drawable(object):
    #initializes the drawable. hskpg
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
    
    #draws the drawable
    #screen (paygame display) - screen to draw to
    #offsetPos (tuple) - offset vector for the drawing (if necessary)
    def draw(self,screen,offsetPos=(0,0)):
        #draw the image if theres something to draw, and similar for the maskimage
        if(self.img):
            screen.blit(self.img,(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y]))
        if(self.maskImg):
            screen.blit(self.maskImg,(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y]))
    
    #moves to tile a certain amount
    #change (tuple) - the vector to shift the tile
    def move(self, change):
        newPos = (self.pos[X]+change[X],self.pos[Y]+change[Y])
        self.pos = newPos

#A drawable, attributable Tile object, to be used on a tilemap - extends Drawable
#attributes (dict) - a dictionary of tile attributes to assign to the tile
#pos (tuple) - absolute position of the tile
#img (pygame Surface) - the image for the Tile
#maskFrames (list) - list of frames for the any visual masking that may occur
class Tile(Drawable):
    #initializes the tile. mostly hskpg. 
    def __init__(self,attributes,pos=(0,0),img=None,maskFrames=None):
        self.setAttributes(attributes)
        
        #if the tile can be hit, init its HP
        if (self.attributes.has_key('hits')):
            self.attributes['hp']=self.attributes['hits']
        
        super(Tile, self).__init__(pos,img,maskFrames) #SUPER TO DRAWABLE!
    
    #sets the tiles attributes (but first makes a copy)
    #attributes (dict) - the new attributes to be set 
    def setAttributes(self,attributes):
        #make a copy of the attributes so they can be modifed and not affect other tiles using the same ones
        self.attributes = attributes.copy()
    
    #change the tile, both attributes and image
    #newAtt (dict) - the new attributes
    #newImg (pygame Surface) - the new image
    def change(self,newAtt,newImg):
        self.setAttributes(newAtt)
        self.img = newImg
    
    #hit the tile for a certain amount of damage
    #dmg (int) - the amount of damage to deal to the tile
    #returns - the tiles value if it breaks, or None if you cant hit the tile
    def hit(self,dmg):
        #if the tile has hp, hit it!
        if (self.attributes.has_key('hp')):
            self.attributes['hp']-=dmg
           
            #if hp hits 0, reset the mask and return its value
            if(self.attributes['hp']<=0):
                self.maskImg=None
                return self.attributes['value']
            
            #if there are mask imgs, determine which mask img to use based on the state of the hp & number of mask frames
            if(self.maskSet):
                #small note - cast hits to float to force float division in py2.7
                maskState=int(len(self.maskSet)/(float(self.attributes['hits'])/self.attributes['hp']))
                self.maskImg=self.maskSet[-maskState-1]    
        
        return None

#A list of images split up from a master image
#imgFile (str) - name of the master imagefile
#imgSize (tuple) - the size of each image in the imageset
#transColor (Color) - the color to draw transparent
class ImageSet(list):
    #initializes the imageset - loads the imageset master image and splits it up
    def __init__(self,imgFile,imgSize,transColor=None,offset=(0,0)):
        self.imgSize = imgSize
        self.offset = offset
        self.transColor = transColor
        
        #load imageset image from file
        self.img = loadImage(imgFile,transColor)
        
        self.load()
    
    #loads the imageset - splits up the master image into a list
    def load(self):
        #get the size of the master image, and the number of tiles it contains
        size=self.img.get_size()
        xTiles = int(size[X] / (self.imgSize[X] + self.offset[X]))
        yTiles = int(size[Y] / (self.imgSize[Y] + self.offset[Y]))
        
        #for each column of tiles
        for y in range(0,yTiles):
            #and for each row of tiles
            for x in range (0,xTiles):
                #get the rectangle to steal the tile image from (x,y,width,height)
                tileRect = (x*self.imgSize[X]+x*self.offset[X],
                            y*self.imgSize[Y]+y*self.offset[Y],
                            self.imgSize[X],
                            self.imgSize[Y])
                
                #steal the tile image & add it to the tileset list
                self.append(self.img.subsurface(tileRect))
 
#a list of images split up from a master image (similar to imageSet), but based on a template
#setImg (pygame Surface) - the image to split up
#frameSize (tuple) - size of each indiividual frame
#setTemplate (3d list) - the image template
class SpriteSet(list):
    #initializes the spriteset - creates a 3d array (action,direction,frame) to act as an image set for the sprite
    def __init__(self,setImg,frameSize,setTemplate):
        self.setImg=setImg
        self.frameSize = frameSize
        
        #loop through each "act" in the set value template
        for act in range(0,len(setTemplate)):
            self.append(list())
            
            #loop through each direction in the sprite set value template
            for direction in range(0,len(setTemplate[act])):
                self[act].append(list())
                
                #loop through each frame in the sprite set value template
                for frame in range(0,len(setTemplate[act][direction])):
                    #pulls the frame number from the frame-string
                    frameNum = int(re.sub(r'[^\d]+','0',setTemplate[act][direction][frame]))
                    
                    #get the Rect to extract the frame from
                    frameRect = (frameNum*frameSize[X],
                                 0,
                                 frameSize[X],
                                 frameSize[Y])
                    frameImg = setImg.subsurface(frameRect) #extracts the frame from the master spriteset image
                    
                    #if the frame needs to be flipped (frame-string contains the flip val), flip the frame
                    if (FLIPVAL in setTemplate[act][direction][frame]):
                        frameImg = pygame.transform.flip(frameImg,True,False)
                    
                    self[act][direction].append(frameImg) #add the final product of the frame to the spriteset
                    
#A "tilemap" - a 2d list (col,row) of tiles objects, and container for game sprites
#tileset (list) - imageset for the tiles comprising the map
#tileSize (tuple) - the size of each tile
#player (Miner) - the player
#tileMaskSet (list) - an image set list for any tile masks
class TileMap(list):
    #initializes the map - creates the tilemap with actual from the given value template
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
    
    #clears a particular mob
    #mobIndex - the position in the mob array to clear out
    def clearMob(self,mobIndex):
        self.mobs.pop(mobIndex)
    
    #add mobs to the map
    #mobs (list of Mob) - list of mobs to add
    def addMobs(self,mobs):
        for mob in mobs:
            self.mobs.append(mob)
    
    #attempts to "move" the map (shift its position on the screen)
    #shift (tuple) - the amount to move
    #min (tuple) - the minimum allowed absolute position for the top left corner
    #max (tuple) - the maximum allowed absolute position for the bottom right corner
    def move(self,shift,min=None,max=None):
        #adjusts shift vector based on bounds for shifting
        if (min): #minumum bound 
            if (self[0][0].pos[Y]+self.shift[Y]>=min[Y] and shift[Y]>0):
                shift=(shift[X],0)
            if (self[0][0].pos[X]+self.shift[X]>=min[X] and shift[X]>0):
                shift=(0,shift[Y])
                
        if (max): #maximum bound
            if (self[-1][-1].pos[Y]+self.shift[Y]+self.tileSize[Y]<=max[Y] and shift[Y]<0):
                shift=(shift[X],0)
            if (self[-1][-1].pos[X]+self.shift[X]+self.tileSize[X]<=max[X] and shift[X]<0):
                shift=(0,shift[Y])
                
        self.shift = (self.shift[X]+shift[X],self.shift[Y]+shift[Y])
    
    #draws the map, row by row, column by column. also draws the player and any mobs on the map
    #screen - the screen to draw to
    def draw(self,screen):
        #draw tile row by row, column by column
        for row in self:
            for tile in row:
                #make sure the tile is visible (in the screen area) before drawing it
                if (tile.pos[X]+self.shift[X]>=-self.tileSize[X] and tile.pos[X]+self.shift[X]<=screen.get_width()):
                    if (tile.pos[Y]+self.shift[Y]>=-self.tileSize[Y] and tile.pos[Y]+self.shift[Y]<=screen.get_height()):
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
    
    #get a tile at a particular position (tile based)
    #pos - tile based position
    #returns - the tile at that position
    def getTile(self,pos):
        return self[pos[Y]][pos[X]]
    
    #gets the absolute size of the map
    def getAbsSize(self):
        return (len(self[0])*self.tileSize[X],len(self)*self.tileSize[Y])
    
    #gets the tile-based size of the map
    def getSize(self):
        return (len(self[0]),len(self))
    
    #gets the 4 surrounding tiles of a given pos
    #pos (tuple) - the position to get surrounding tiles from (tile based)
    #returns - list of surrounding tiles, or None if there was an error
    def getNearTiles(self,pos):
        #FIX - unknown bug here that i cant consistently reproduce (tries to access a tile that isnt on the map?).
        #...just return null if it arises
        try:
            #in order of R L U D
            return [self[pos[Y]][pos[X]+1],self[pos[Y]][pos[X]-1],self[pos[Y]-1][pos[X]],self[pos[Y]+1][pos[X]]]
        except IndexError:
            return None

#A map template reader that reads a map template from an external file and puts it into a 2d list
#mapFile (str) - name of the external map file (each row on a new line)
#dlim (str) - the delimieter for the columns in the mapfile
class mapReader(list):
    #initalizes the mapreader. hskpg
    def __init__(self,mapFile,dlim='\t'):
        self.mapFile=mapFile
        self.dlim=dlim
        
        self.load() #loads the map template from the file
    
    #loads the map template from the given file
    def load(self):
        #open the file for reading
        readFile = open(self.mapFile,'r')
        
        #for each line in the file
        for line in readFile:
            #strip out any newline characters
            line = line.rstrip()
            
            #split it up based on the dlim, and add it to the mapReader
            self.append(str(line).split(self.dlim))

#a map template that is generated at (weighted) random from a list of possible map tiles and then put it into a 2d list
#size (tuple) - the size of the desired random map template (x,y)
#tileTemplates (dict) - a dictionary holding many different tile variables (chance to be used,type of tile, etc etc)
class randomMapTemplate(list):
    #intializes the tilemap - randomly places tiles using a weighted algorithm
    def __init__(self,size,tileTemplates):
        self.size=size
        
        #for weighted random item selection algorithm - sums up total chance
        chanceSum = 0;
        for cs in tileTemplates.keys():
            chanceSum+=tileTemplates[cs]['chance']
        
        #create the random tilemap, row by row, col by col
        for row in range(0,self.size[Y]):
            self.append(list())
            
            for col in range(0,self.size[X]):
                rnd = random.randint(0,chanceSum) #generate the random tilevalue based on the weighted chance
                lowest=0
                
                #loop through each tile in the tile templates to determine if the random chance has selected it
                for c in tileTemplates.keys():
                    chance = tileTemplates[c]['chance']
                    if(rnd<chance): #if so, set it and go to the next column
                        self[row].append(c)
                        break
                    rnd-=chance

    #sets the border of the tilemap template to a particular value
    #borderVal - the value to set the border to
    def setBorder(self,borderVal):
        for top in range(0,len(self[0])):
            self[0][top]=borderVal
        
        for bottom in range(0,len(self[-1])):
            self[-1][bottom]=borderVal
        
        #left and right sides
        for row in self:
            row[0]=borderVal
            row[-1]=borderVal
           
    #sets (overwrites) a particular area of the tilemap template from a given template
    #startPos (tupl) - position to start at
    #template (list) - the tilemap template to set
    def setArea(self,startPos,template):
        for row in range(0,len(template)):
            for col in range(0,len(template[row])):
                self[row+startPos[Y]][col+startPos[X]]=template[row][col]      

#A animated drawable - basically an acting sprite (a character) for the game
#pos - the original position for the miner
#spriteset - the imageset to be used for the miner
#stats (dict) - various stats for the miner
class Miner(Drawable):
    #initializes the miner, creating any necessary stats and animation variables.
    def __init__(self,pos,spriteset,stats):
        #setup basic state variables
        self.dir = DIR_RIGHT
        self.act = ACT_NONE
        self.frame = 0
        self.maskFrame=0
        self.spriteset = spriteset
        self.stats = stats
        
        if(STAT_MAXBAG in self.stats.keys()):
            self.stats[STAT_ORIGINAL_BAG]=self.stats[STAT_MAXBAG]
            self.stats[STAT_BAG]=list()
        
        #get the absolute position of the miner (framesize*given pos)
        absPos = (pos[X]*spriteset.frameSize[X],pos[Y]*spriteset.frameSize[Y])
        super(Miner, self).__init__(absPos,spriteset[self.act][self.dir][self.frame])
        
        #setup antimation-related timer variables
        self.lastMod = pygame.time.get_ticks()
        self.maskMod = pygame.time.get_ticks()
        
        #update the players overall stats (bag size, delay time, etc)
        self.updateStats()
    
    #adds a particular value to the players bag...if it can fit & if its worth something
    #value (int) - the value to add to the bag
    #returns - true if the addition could fit and had value, false otherwise
    def addToBag(self,value):
        #if the bag still has space , and its actually worth something
        if (len(self.stats[STAT_BAG])<self.stats[STAT_MAXBAG] and value>0):
            self.stats[STAT_BAG].append(value)
            return True #all done - it worked
        else: #if it cant fit or its not worth jack, return false
            return False
    
    #clears out the bag and returns its overall value
    #returns - the total value of the bag
    def clearBag(self):
        bagVal=0
        
        #goes through each value in the bag, adds it to the bag value, and clears it out
        for v in range(0,len(self.stats[STAT_BAG])):
            bagVal+=self.stats[STAT_BAG].pop()
        
        return bagVal
        
    #controls animation of the miner
    #elapsed - time elapsed since the last animation
    #delay - the time that should elapse before the next animation
    #returns - true if its time to animate and the miners actually meant to be animating currently, false otherwise
    def animate(self, elapsed, delay):     
        if(self.act>=ACT_NONE):
            #if enough time has passed sine the last animation
            if (elapsed - self.lastMod > delay):
                self.frame += 1 #move to the next frame
                
                #if there is no more frames, go back to 0
                if self.frame >= len(self.spriteset[self.act][self.dir]):
                    self.frame = 0
                    
                #change the current image to the current frame
                self.img = self.spriteset[self.act][self.dir][self.frame]
                self.lastMod=elapsed
                return True
        return False     
    
    #updates all the players complex stats (e.g. max bag size, animation delays) based on the base stats (str, speed)
    def updateStats(self):
        #calculate maximum bag size based on str
        if(STAT_MAXBAG in self.stats.keys()):
            self.stats[STAT_MAXBAG]=self.stats[STAT_ORIGINAL_BAG] + self.stats[STAT_STR]
        
        #calculate frame/action delays based on speed
        self.frameDelay = SPRITE_FRAME_DELAY / self.stats["sp"]
        self.actDelay = SPRITE_ACT_DELAY / self.stats["sp"]
    
    #adds a value to a particular stat if it exists
    #stat (str) - the stat to add to
    #val (int) - the amount to add
    def addStat(self,stat,val):
        if (stat in self.stats.keys()):
            self.stats[stat]+=val
            self.updateStats() #update the complex stats
    
    #substracts a value to a particular stat if it exists
    #stat (str) - the stat to subtractr from
    #val (int) - the amount to subtract
    def subStat(self,stat,val):
        if (stat in self.stats.keys()):
            self.stats[stat]-=val
            
            #dont let the stat go lower than 0
            if(self.stats[stat]<0):
                self.stats[stat]=0

            self.updateStats() #update the complex stats
    
    #updates the player - basically a handler for the animation logic
    #returns - act (int) if the miner has completed his action/animation
    #        - step distance (tuple) if the miner has moved but didnt complete the act
    #        - None otherwise
    def update(self):
        returnAct = self.act
        
        #if the miner is currently doing something
        if (self.act>ACT_NONE):
            #try to animate. if its time...
            if (self.animate(pygame.time.get_ticks(),self.frameDelay)):
                self.move(self.stepDist) #move the miner any necessary distance
                
                #if the action is complete (all frames been played)
                if(self.frame==0):
                    self.lastMod+=self.actDelay #delay the next action by adelay milliseconds
                    
                    #reset for next act
                    self.act=0
                    self.stepDist=0
                    
                    return returnAct;
                
                #if we moved but didn't complete the act return the distance tuple
                if(self.stepDist!=(0,0)):
                    return (self.stepDist)
        
        return None
    
    #animate any mask image set (e.g. effect) on the miner
    #elapsed - time elapsed since last animation
    #delay - time delayed between each animation
    #returns - true if the animation is complete, false otherwise
    def animateMask(self,elapsed,delay):
        #if the time necessary has elapsed
        if (elapsed - self.maskMod > delay):
            self.maskFrame += 1 #go to the next mask frame
            if self.maskFrame >= len(self.maskSet): #if we've reached the end of the mask image set
                #go back to the start and return that were done
                self.maskFrame = 0 
                return True
            
            #change the mask image based on its current frame
            self.maskImg = self.maskSet[self.maskFrame]
            self.maskMod=elapsed
        return False     
    
    #updates the mask - basically a handler for the mask animation logic
    #returns true when the mask has completed animating through its frames, false until that point
    def updateMask(self,maskSet,frameDelay):
        #if this is a new maskSet, store it
        if(self.maskSet!=maskSet):
            self.maskSet=maskSet
        
        #try to animate the mask - when its done, return success   
        if (self.animateMask(pygame.time.get_ticks(),frameDelay)):
            self.maskImg=None
            return True
        
        return False
    
    #set the direction of the player - currently dir is only used for visual appearances, as the player can only look left and right in this game
    #_dir - new direction of the player
    def setDir(self,_dir):
        #if the miner isnt current busy and its actually a change of direction
        if(self.act==ACT_NONE and self.dir!=_dir):
            self.dir=_dir
            self.img = self.spriteset[self.act][self.dir][self.frame]
    
    #attempts to perform an action - just sets up necessary action variables
    #action (int) - the action to perform
    #dist (tuple) - the distance to be travelled during this action...only used for walking currently
    def doAction(self,action,dist=(0,0)):
        #if the miner isnt already acting
        if(self.act==ACT_NONE):
            self.act=action #set the action in place
            numFrames = len(self.spriteset[self.act][self.dir])
            
            #determine each step distance for the number of frames for the given action
            self.stepDist = (dist[X]/numFrames,dist[Y]/numFrames) 
            return True
        return False
    
    #gets the miners current image (frame)
    def getImg(self):
        return self.spriteset.getImg()
    
    #gets the players current position (tile based, not absolute)
    def getPos(self):
        return (self.pos[X]/self.spriteset.frameSize[X],self.pos[Y]/self.spriteset.frameSize[Y])

#A very simple target-based AI
#target (Miner) - the target of the AI
class AI(object):
    #intializes the AI
    def __init__(self,target):
        self.target=target
    
    #based on the AI's own position in space as well as the players, and what 4 tiles are surrounding it, it will choose a direction to act towards
    #myPos (tuple) - the AI's position
    #nearTiles (list) - the 4 tiles surrounding the AI currently
    def chooseDir(self,myPos,nearTiles):
        #if there are "near tiles" (FIX - for bug)
        if(nearTiles):
            targetPos=self.target.pos #gets the targets position
            chkOrder=list()
            
            #determines the "check order" to check the surrounding tiles in based on the targets position
            if(myPos[Y]>targetPos[Y]):
                chkOrder = AI_CHECKORDER[DIR_UP]
            elif(myPos[X]<targetPos[X]):
                chkOrder = AI_CHECKORDER[DIR_RIGHT]
            elif(myPos[Y]<targetPos[Y]):
                chkOrder = AI_CHECKORDER[DIR_DOWN]
            elif(myPos[X]>targetPos[X]):
                chkOrder = AI_CHECKORDER[DIR_LEFT]
            
            #check each surrounding in the "check order"
            for direction in chkOrder:
                #check the direction to make sure its not blocked, if not, return it
                if(nearTiles[direction].attributes['type']!=MINE_BLOCK_FULL):
                    return direction
            
        return DIR_LEFT #default to trying to go left - doesn't matter, AI cant move

#SEE MINER - A miner that has its own ai to control its actions
#pos - the original position for the mob
#spriteset - the imageset to be used for the mob
#stats (dict) - various stats for the mob
#target (Miner) - the target for the mobs AI
class Mob(Miner):
    #intializes the Miner Mob
    def __init__(self,pos,spriteset,stats,ai):
        self.ai=ai #assigns the given AI
        super(Mob, self).__init__(pos,spriteset,stats) #SUPER TO MINER!
    
    #runs the AI routine - find a direction to act towards
    #nearTiles (list) - the 4 tiles surrounding the Mob
    #returns - the new direction to move in/act towards, chosen by the AI
    def runAI(self,nearTiles):
        #AI chooses a direction based on the nearest tiles
        newDir = self.ai.chooseDir(self.pos,nearTiles)
        
        #if its right or left, change the mobs visual sprites direction
        if(newDir==DIR_RIGHT or newDir==DIR_LEFT):
            self.setDir(newDir)
            
        return newDir
    
    #the mob is dying! call the mask update to animate
    #deathSet (list) - the list of frames for the death animation
    #frameDelay (int) - the delay between frames for the death animation
    #returns true if the animation is complete, none otherwise
    def dying(self,deathSet,frameDelay):
        return self.updateMask(deathSet,frameDelay)

#A UI Button object that will automatically resize itself to fit its text and can be clicked
#name (str) - the name of the button, to help higher levels identify it when its been clicked
#pos (tuple) - the absolute position of the button in its container
#btnSet (list) - the image set for the button
#textImg (pygame Surface) - the image for the text to be drawn onto the button
class Button(object):
    #intializes the button and creates the btn image necessary to fit the given text
    def __init__(self,name,pos,btnSet,textImg):
        self.pos = pos
        self.name = name
        
        #get required size of mid-section of button
        pnlSize=btnSet[0].get_size()
        textWidth = int(math.ceil(textImg.get_width()/float(pnlSize[X]))) #force float division
        self.size=((2+textWidth)*pnlSize[X],pnlSize[Y])  #get size of button
        
    #Compile the btnSet and textImg into one image =======================
        self.img=pygame.Surface(self.size)
        drawPos=(0,0)
        self.img.blit(btnSet[BTNSET_IMG_LEFT],drawPos) #draw left border of button

        #draw middle portion of button
        for w in range(0,textWidth):
            #+1 to accoutn for left border img
            drawPos=((1+w)*pnlSize[X],0)
            self.img.blit(btnSet[BTNSET_IMG_MID],drawPos)
        
        self.img.blit(btnSet[BTNSET_IMG_RIGHT],(self.size[X]-pnlSize[X],0)) #draw right border of button
        
        #get middle of img and try to center the text, then draw it to the buttons img
        textPos = ((self.size[X]/2.0)-(textImg.get_width()/2.0),(self.size[Y]/2.0)-(textImg.get_height()/2.0)) #force float divison
        self.img.blit(textImg,textPos)
    # image done =========================================================
    
    #draws the button
    #screen (pygame Surface) - the screen to draw to
    #pos (tuple) - the position of the container on the screen
    #window (Window) - the window container, if any
    def draw(self,screen,pos,window=None):
        if (window): #if its contained in a window, check/fix for any UI alignments
            self.pos=specialPos(self.pos,window.size,self.size)
        screen.blit(self.img,(self.pos[X]+pos[X],self.pos[Y]+pos[Y])) #draw the button
    
    #determines if this button was clicked
    #mousePos (tuple) the position of the mouse click
    #offsetPos (tuple) - the offset position of the container
    #returns true if clicked, false otherwise
    def click(self,mousePos,offsetPos):
        realPos=(self.pos[X]+offsetPos[X],self.pos[Y]+offsetPos[Y])
        
        if (realPos[X]<mousePos[X] and realPos[X]+self.size[X]>mousePos[X]):
            if (realPos[Y]<mousePos[Y] and realPos[Y]+self.size[Y]>mousePos[Y]):
                return True
        return False

#A simple UI label to display text
#pos (tuple) - the absolute position of the label in its container
#text (str) - labels text
#font (pygame Font) - Font to be used in the label
#color (Color) - color of text
#transColor - for text transparency...not currently used
class Label(object):
    #initializes the label. mostly hskpg
    def __init__(self,pos,text,font,color,transColor=None):
        #HSKPG
        self.pos=pos
        self.color=color
        self.font=font
        self.text=text
        self.transColor=transColor
        
        #creates a new label image from the given parameters
        self.newImg(textImage(text,font,color,transColor))

    #sets the labels images and gets its size
    #newImg (pygame Surface) - the new image for the label
    def newImg(self,newImg):
        self.img=newImg
        self.size=self.img.get_size()
    
    #change some textual attribute of the label
    #text (str) - text to change to
    #font (pygame Font) - font to change to
    #color (pygame Color) - color of font to change to
    def change(self,text=None,font=None,color=None):
        #determine which attributes of the label are being changed
        if(text):
            self.text=text
        if(font):
            self.font=font
        if(color):
            self.color=color
        
        #create the img from the new text, and set the new img
        self.newImg(textImage(self.text,self.font,self.color,self.transColor))
    
    #draws the label
    #screen (pygame Surface) - the screen to draw to
    #pos (tuple) - the offset drawing position of its container (cant be passed with container)
    #window (Window) - the window container itself
    def draw(self,screen,pos,window=None):
        #makes any necessary last-minute changes to the position for spcial UI-alignment if its within a window
        if (window):
            self.pos=specialPos(self.pos,window.size,self.size)
        screen.blit(self.img,(self.pos[X]+pos[X],self.pos[Y]+pos[Y])) 

#A UI "Window" (message box-style) that can be clicked
#pos (tuple) - the position of the window in its container
#winSet (list) - the imageset to be used for the window (always top and bottom)
#numPanels (int) - the number of middle panels to be used for the window (middle of winSet)
#title (str) - the title for the window - appears in big at the top
#labels (list) - list of Label objects to put in the window
#btns (list) - list of Button objects to put in the window
class Window(object):
    #initializes the window. mostly hskpg
    def __init__(self,pos,winSet,numPanels,title=None,labels=None,btns=None):
        #HSKPG
        self.winSet=winSet
        self.pnlSize=self.winSet[0].get_size() #only works if all panels are the same size
        self.title=title
        self.labels=labels
        self.btns=btns
        self.pos=pos
        self.visible=True
        
        #create the panels for the window & get its overall size
        self.createPanels(numPanels)
        self.size = (self.pnlSize[X],self.pnlSize[Y]*(numPanels + 2))
        
    #creates the necessary panels and appends them to a list (always top and bottom + 1 if theres a title + numPanels)
    #numPanels (int) - see above equation
    def createPanels(self,numPanels):
        self.panels=list()
        self.panels.append(self.winSet[WINSET_IMG_TOP]) #add top panel (window border)
        
        if(self.title): #add an extra panel if theres a title
            self.title=textImage(self.title,WIN_TITLE_FONT,WIN_FONT_COLOR)
            self.panels.append(self.winSet[WINSET_IMG_PNL])
        
        #add middle panels
        for p in range(0,numPanels):
            self.panels.append(self.winSet[WINSET_IMG_PNL])
            
        self.panels.append(self.winSet[WINSET_IMG_BTM]) #add bottom panel (window border)
    
    #draws the Window and anything contained within it
    #screen - the game screen to draw to
    def draw(self,screen):
        #make sure window is visible before trying to draw it
        if (self.visible):
            #perform any special UI alignment necessary for drawing
            drawPos=specialPos(self.pos,screen.get_size(),(self.pnlSize[X],self.pnlSize[Y]*len(self.panels)))
    
            #draw each panel
            for p in range(0,len(self.panels)):
                screen.blit(self.panels[p],(drawPos[X],drawPos[Y]+p*self.pnlSize[Y]))
            
            #draw title if necessary
            if(self.title):
                #centers the tile on the top two panels
                titlePos = (self.pnlSize[X]/2.0 - self.title.get_width()/2.0 +drawPos[X],self.pnlSize[Y] - self.title.get_height()/2.0 + drawPos[Y])#force float divison
                screen.blit(self.title,titlePos)
            
            #draw all the labels
            if (self.labels):
                for label in self.labels:
                    label.draw(screen,drawPos,self)
    
            #draw all the buttons
            if(self.btns):
                for btn in self.btns:
                    btn.draw(screen,drawPos,self)
    
    #determines if any buttons have been clicked in the window
    #screen (pygame Surface) - the screen being clicked on
    #pos (tuple) - the position of the mouseclick
    #returns - name of button that was clicked, or false if nothing was clicked
    def click(self, screen, mousePos):
        #check for any centering the window may partake in
        winPos=specialPos(self.pos,screen.get_size(),(self.pnlSize[X],self.pnlSize[Y]*len(self.panels)))
        
        #first, check to see if the windowi s visible before checking for clicks
        if(self.visible):
            #loop through all tghe windows buttons to see if any were clicked
            for btn in self.btns:
                if (btn.click(mousePos,winPos)): #if the button was clicked, return true
                    return btn.name
        #false if nothing wasnt clicked
        return False