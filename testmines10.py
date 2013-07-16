#import needed modules for pygame
import pygame, sys
from pygame.locals import *

#initialize pygame
pygame.init()
pygame.font.init()

from gameConstants import *
from gameFunctions import *
from gameObjects import *

#Create any constants that require game objects
#windows image set for drawing windows
WINSET_PNLSIZE=(350,20)
WINSET = TileSet(IMG_WINSET,WINSET_PNLSIZE,TILE_TRANSCOLOR)
#button imageset for drawing buttons
BTNSET_PNLSIZE=(20,20)
BTNSET=TileSet(IMG_BTNSET,BTNSET_PNLSIZE,TILE_TRANSCOLOR)

#label text for the shop items
SHOP_LABELS=["Strength  $"+str(SHOP_COST_STR),
            "Speed     $"+str(SHOP_COST_SP)]



                
#=========================================================================================
#                     MAIN/GAME FUNCTIONS
#=========================================================================================            

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
    
        if(nextTile.getAttributes()['type']==MINE_BLOCK_FULL):
            pass
        elif (direction==DIR_UP and tilemap.getTile(nextPos).attributes['type']==MINE_BLOCK_UP):
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

def createStatWin(player):
    #ui elements for stats window
    statLbls = [Label("Strength: " + str(player.stats['str']),WIN_FONT_SMALL,WIN_FONT_COLOR,(80,0)),
                Label("Speed   : " + str(player.stats['sp']),WIN_FONT_SMALL,WIN_FONT_COLOR,(80,18)),
                Label("Bag     : " + str(len(player.stats['bag'])) + " / " + str(player.stats['maxBag']),
                      WIN_FONT_SMALL,WIN_FONT_COLOR,(190,0)),
                Label("Money   : " + str(player.stats['money']),WIN_FONT_SMALL,WIN_FONT_COLOR,(190,18))]
    statWin = Window((ALIGN_CENTER,ALIGN_BOTTOM),WINSET,0,None,statLbls)
    
    return statWin

def createShopWin():
    # ui elements for the shops items
    shopLbls=[Label(SHOP_LABELS[0],WIN_FONT,WIN_FONT_COLOR,(60,35)),
              Label(SHOP_LABELS[1],WIN_FONT,WIN_FONT_COLOR,(60,60))]
    shopBtns=[Button((200,45),BTNSET,textImage(SHOP_BTN_TEXT,BTN_FONT,WIN_FONT_COLOR)),
              Button((200,70),BTNSET,textImage(SHOP_BTN_TEXT,BTN_FONT,WIN_FONT_COLOR))]
    
    #setup window for shopping    
    return Window((ALIGN_CENTER,5),WINSET,len(SHOP_LABELS),SHOP_TITLE,shopLbls,shopBtns)

#main game loop - runs until the user quits
# screen - 
def game(screen):
    #load the spriteset image for the player (miner)
    playerImg=loadImage(IMG_PLAYER,TILE_TRANSCOLOR)
    
    #setup and create the player
    player = Miner(PLAYER_POS,SpriteSet(playerImg,(48,48),SPRITE_TEMPLATE),PLAYER_STATS.copy())
    
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
    zombies=createZombies(tilemap,tileset,SPRITE_TEMPLATE,player,(1,len(aboveground))) 
    tilemap.addMobs(zombies)
    
    #setup the fire spriteset for any zombies that need to burn!
    fireImg=loadImage(IMG_FIRE,TILE_TRANSCOLOR)
    fireTemplate=[[['0','1','2','^1','3','^2','0','3','2']]] #uses a template/spriteset so it can have duplicates of frames 
    fireSet=SpriteSet(fireImg,(48,48),fireTemplate)[0][0] #spritesets are dicts, but we only need the first "act"+"dir" of it for this (which is a list)
    
    #setup the shop window
    shopWin=createShopWin()
    
    #setup window for stats
    statWin = createStatWin(player)
    
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
                else:
                    break #ignore other keyboard inputs
                
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
            if (tilemap.getTile(zombie.getPos()).attributes['type']==MINE_BLOCK_UP):
                #dying animation. when the animation is complete, remove the zombie from the tilemap and the game
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
        statWin.draw(screen)
        if(tilemap.getTile(player.getPos()).attributes['type']==MINE_SHOP):
            shopWin.draw(screen)
            
        pygame.display.flip()
    
    
#main program - sets up pygame & controls between-scren flow (mainmenu, game)
def main():
    #setup game screen
    gameScreen = pygame.display.set_mode((400,450))
    
    #start the game
    game(gameScreen);

#Start program
if __name__ == "__main__":
    main()