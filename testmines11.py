#import needed modules for pygame
import pygame, sys
from pygame.locals import *

#initialize pygame
pygame.init()
pygame.font.init()

#import constants, functions, and objects needed for the game
from gameConstants import *
from gameFunctions import *
from gameObjects import *

#Create any constants that require game objects to first be imported
#windows image set for drawing windows
WINSET_PNLSIZE=(350,20)
WINSET = TileSet(IMG_WINSET,WINSET_PNLSIZE,TILE_TRANSCOLOR)
#button imageset for drawing buttons
BTNSET_PNLSIZE=(20,20)
BTNSET=TileSet(IMG_BTNSET,BTNSET_PNLSIZE,TILE_TRANSCOLOR)

#label text for the shop items
SHOP_LABELS=["Strength  $"+str(SHOP_COST_STR),
             "Speed     $"+str(SHOP_COST_SP)]

#menu buttons - button id's and button text
MENU_BTN_PLAY = "Play"
MENU_BTN_HOW = "Instructions"
MENU_BTN_EXIT = "Exit"
MENU_BTN = "Return to Menu"
MENU_TITLE = "Main Menu"

                
#=========================================================================================
#                     MAIN/GAME FUNCTIONS
#=========================================================================================            

def tryAction(screen,miner,direction,tilemap):
    #get the direction vector for the desired action
    if(direction==DIR_RIGHT):
        move=(1,0)
    elif(direction==DIR_LEFT):
        move=(-1,0)
    elif(direction==DIR_UP):
        move=(0,-1)
    elif(direction==DIR_DOWN):
        move=(0,1)
    
    #determine the next tile position in the desired direction
    nextPos = (miner.getPos()[X]+move[X],miner.getPos()[Y]+move[Y])
    
    #make sure the next position to be acted towards is within the screens dimensions
    if(nextPos[X]>=0 and nextPos[X]<tilemap.getSize()[X] and
       nextPos[Y]>=0 and nextPos[Y]<tilemap.getSize()[Y]):
        nextTile = tilemap.getTile(nextPos) #get the next tile in the chosen direction
        
        #if new direction next tileis blocked...
        if(nextTile.getAttributes()['type']==MINE_BLOCK_FULL):
            pass #can't walk in that direction
        
        #if new direction is up, but up is blocked...
        elif (direction==DIR_UP and tilemap.getTile(nextPos).attributes['type']==MINE_BLOCK_UP):
            pass #can't act in that direction
        
        #if the new direction is diggable
        elif (nextTile.getAttributes()['type']==MINE_DIGGABLE):
            if(miner.doAction(ACT_DIG)): #dig it and return the tile being dug
                return nextTile
        
        else: #if the new direction is free and the player is trying to move
            if(miner.doAction(ACT_WALK,(move[X]*tilemap.getTileSize()[X],move[Y]*tilemap.getTileSize()[Y]))):
                return nextTile
            
def scrollMap(screen,player,tilemap,moveVect):
    #if the player has reached an edge of the map on the x-axis, dont move the map in that direction anymore
    if (player.getPos()[X]<3 or player.getPos()[X]>tilemap.getSize()[X]-3 or player.getPos()[X]==3 and player.dir==DIR_RIGHT):
        moveVect=(0,moveVect[Y])
    
    #if the player has reached an edge of the map on the y-axis, dont move the map in that direction anymore
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
        
        #create a new zombie and add it to the list of zombies
        zombie = Mob(randomPos,SpriteSet(zombieImg,(48,48),spriteTemplate),zombieStats,zombieAI)
        zombies.append(zombie)
        
        #change the tile to be a "broken" one at the randomly chose position
        tilemap.getTile(randomPos).change(mines[MINE_DUG],tileset[MINE_DUG])
    
    return zombies

def createStatWin(player):
    #ui elements for stats window
    statLbls = [Label((80,0),"Strength: " + str(player.stats['str']),WIN_FONT_SMALL,WIN_FONT_COLOR),
                Label((80,18),"Speed   : " + str(player.stats['sp']),WIN_FONT_SMALL,WIN_FONT_COLOR),
                Label((190,0), "Bag     : " + str(len(player.stats['bag'])) + " / " + str(player.stats['maxBag']),
                      WIN_FONT_SMALL,WIN_FONT_COLOR),
                Label((190,18),"Money   : " + str(player.stats['money']),WIN_FONT_SMALL,WIN_FONT_COLOR)]
    
    #create the stat window
    statWin = Window((ALIGN_CENTER,ALIGN_BOTTOM),WINSET,0,None,statLbls)
    
    return statWin

def buyStat(player,stat,cost):
    #if the player can afford the stat
    if (player.stats['money']>=cost):
        player.addStat(stat,1)
        player.subStat('money',cost)
        return True
    else:
        return False
    
def createShopWin(player):
    # ui elements for the shops items
    shopLbls=[Label((60,35),SHOP_LABELS[0],WIN_FONT,WIN_FONT_COLOR),
              Label((60,60),SHOP_LABELS[1],WIN_FONT,WIN_FONT_COLOR)]
    shopBtns=[Button(SHOP_BTN_STR,(200,45),BTNSET,textImage(SHOP_BTN_TEXT,BTN_FONT,WIN_FONT_COLOR)),
              Button(SHOP_BTN_SP,(200,70),BTNSET,textImage(SHOP_BTN_TEXT,BTN_FONT,WIN_FONT_COLOR))]
    
    #setup window for shopping    
    return Window((ALIGN_CENTER,5),WINSET,len(SHOP_LABELS),SHOP_TITLE,shopLbls,shopBtns)

def createMenuWin():
    # ui elements for the main menu buttons
    menuBtns=[Button(MENU_BTN_PLAY,(ALIGN_CENTER,45),BTNSET,textImage(MENU_BTN_PLAY,BTN_FONT,WIN_FONT_COLOR)),
              Button(MENU_BTN_HOW,(ALIGN_CENTER,70),BTNSET,textImage(MENU_BTN_HOW,BTN_FONT,WIN_FONT_COLOR)),
              Button(MENU_BTN_EXIT,(ALIGN_CENTER,95),BTNSET,textImage(MENU_BTN_EXIT,BTN_FONT,WIN_FONT_COLOR))]
    
    #setup window for the main menu  
    return Window((ALIGN_CENTER,ALIGN_CENTER),WINSET,len(menuBtns)+1,MENU_TITLE,None,menuBtns)

def createEndWin(title, msg):
    # ui elements for the shops items
    endLbls=[Label((ALIGN_CENTER,50),msg,WIN_FONT,WIN_FONT_COLOR)]
    endBtns=[Button(MENU_BTN,(ALIGN_CENTER,60),BTNSET,textImage(MENU_BTN,BTN_FONT,WIN_FONT_COLOR))]
    
    #setup window for shopping    
    return Window((ALIGN_CENTER,5),WINSET,len(endLbls)+len(endBtns),title,endLbls,endBtns)

def updateZombies(screen,tilemap,zombies,maskSet,player,zActTile):
    return None;


#main game loop - runs until the user quits
# screen - 
def game(screen):
    #load the spriteset image for the player (miner)
    playerImg=loadImage(IMG_PLAYER,TILE_TRANSCOLOR)
    
    #setup and create the player
    player = Miner(PLAYER_POS,SpriteSet(playerImg,SPRITE_SIZE,SPRITE_TEMPLATE),PLAYER_STATS)
    
    #create the template for the mine map
    template=randomMapTemplate(MAP_SIZE,mines) #create random map template of mines
    template.setBorder(MINE_ROCK) #set the border to be all unbreakable bricks
    aboveground=mapReader('above.txt','\t') #load in custom map for aboveground
    template.setArea((0,0),aboveground) #combine random minemap with aboveground map @ top left corner
        
    #load in the tileset and tile maskset for the game 
    tileset = TileSet(IMG_TILESET,TILE_SIZE,TILE_TRANSCOLOR)
    maskSet = TileSet(IMG_CRACKS,TILE_SIZE,TILE_TRANSCOLOR)

    #create the MineMap (tilemap for the game) and create/add zombies
    tilemap=MineMap(template,tileset,TILE_SIZE,player,maskSet)
    zombies=createZombies(tilemap,tileset,SPRITE_TEMPLATE,player,(1,len(aboveground))) 
    tilemap.addMobs(zombies)

    #setup the fire spriteset for any zombies that need to burn!
    fireImg=loadImage(IMG_FIRE,TILE_TRANSCOLOR)
    fireSet=SpriteSet(fireImg,SPRITE_SIZE,FIRE_TEMPLATE)[0][0] #spritesets are dicts, but we only need the first "act"+"dir" of it for this (which is a list)

    #setup the shop window
    shopWin=createShopWin(player)
    
    #setup window for stats
    statWin = createStatWin(player)
    
    #initialize the "end game" window - if this is set, the game is over
    endWin = None
    
    #set pygame to "repeat" key-presses (basically key toggling)
    pygame.key.set_repeat(50,50)
    
    #play the game for as long as this is true
    play=True
    
    #holder variables for action-affected tiles
    pActTile=None
    zActTile=None
    
    #begin game loop
    while play:
        
        #check all of the events that have occured since last loop
        for event in pygame.event.get():
            #if users quits, exit the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            #if a key was pressed and the game isnt over yet...
            elif (event.type == KEYDOWN and not endWin):
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
                    continue #ignore other keyboard inputs (go to next event)
                
                #try to act on the next tile in the chosen direction
                pTryResult=tryAction(screen,player,direction,tilemap)
                if(pTryResult): #if the action went through, get which tile was affected (or the move vector)
                    pActTile=pTryResult
            
            #if the mouse was clicked, check if any buttons were clicked
            elif event.type == MOUSEBUTTONDOWN:
                #if ending window is shown (game is over), detect clicks for ending window
                if(endWin):
                    clicked=endWin.click(screen,event.pos)
                
                #otherwise, check shop window for clicks
                else:
                    clicked=shopWin.click(screen,event.pos)
                
                #if a button was infact clicked, determine which button and take appropriate actions
                if(clicked):
                    if(clicked==SHOP_BTN_STR):
                        buyStat(player,'str',SHOP_COST_STR) #player bought str
                    elif (clicked==SHOP_BTN_SP):
                        buyStat(player,'sp',SHOP_COST_SP) #player bought sp
                    elif (clicked==MENU_BTN)
                        play=False #game is over (exits game loop) and player returned to main menu
                        break
                        
                    #update the stat window  
                    statWin=createStatWin(player)

        #always clear screen and redraw tilemap - doesn't matter if game is over or not
        screen.fill(Color(0,0,0))
        tilemap.draw(screen)
        
        #if the game isn't over yet, run updates for players and zombies
        if (not endWin):
        
#HANDLE UPDATING PLAYER ======================================================================        
            #update the player and get the returned action data
            playerAct=player.update()
            
            #if the finished act is a tuple (e.g. a move vector)
            if (type(playerAct) is tuple):
                moveVect = playerAct
                #scroll the map the distance that the player has moved
                scrollMap(screen,player,tilemap,moveVect)
            
            #if the player is done walking
            elif (playerAct==ACT_WALK):
                #finish scrolling the distance the player has moved
                scrollMap(screen,player,tilemap,moveVect)
                
            # if the player is done hitting
            elif (playerAct==ACT_DIG):
                pHitTile = pActTile
                pHitResult = pHitTile.hit(player.stats['str'])
    
                #if the hit returned a result (broke?)
                if(pHitResult!=None):
                    pHitTile.change(mines[MINE_DUG],tileset[MINE_DUG]) #set the dug-out tiles attributes and image to "dug" tile
                    
                    #if the player just broke thewinning mine, show the winning game screen
                    if(pHitResult==MINE_VAL_WIN):
                        endWin=createEndWin("Congratulations!","You Win!!")
                        
                    else: #otherwise, if it was a normal tile...
                        player.addToBag(pHitResult) #add the tiles value to the players bag
                        statWin = createStatWin(player) #create a new stat window (basically an update, but i never wrote an update)
#PLAYER UPDATE DONE ==================================================================
            
            
#HANDLE ZOMBIE UPDATING ===============================================================
            #loop through each zombie to update
            for z in range(0,len(zombies)):
                zombie=zombies[z]
                
                #if the zombie is touching the player - game over!
                if (zombie.getPos() == player.getPos()):
                    endWin = createEndWin("Game Over","You have died!")
                
                #otherwise, if the zombie is outside...
                elif (tilemap.getTile(zombie.getPos()).attributes['type']==MINE_BLOCK_UP):
                    #dying animation. when the animation is complete, remove the zombie from the tilemap and the game
                    if(zombie.dying(fireSet,SPRITE_MASK_DELAY)):
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
                if (zombieAct==ACT_DIG):
                    zHitTile = zActTile #get the tile the zombie is trying to hit
                    zHitResult = zHitTile.hit(zombie.stats['str'])
                    
                    #if the hit returned a result (broke?)
                    if(zHitResult!=None):
                        #set the dug-out tiles attributes and image to "dug" tile
                        zHitTile.change(mines[MINE_DUG],tileset[MINE_DUG]);
#ZOMBIE UPDATING DONE ===================================================================
        
    
#HANDLE WINDOW DRAWING =====================================================================
            #if the player is sitting on a shop tile, show shop!
            if(tilemap.getTile(player.getPos()).attributes['type']==MINE_SHOP):
                player.addStat('money',player.clearBag()) #exchange bag for moneys
                statWin=createStatWin(player) #update the stat window
                shopWin.visible=True
            else:
                shopWin.visible=False
            
            statWin.draw(screen)
            shopWin.draw(screen)
        
        #if the game is over(endWin is defined), show the end game window
        else:
            endWin.draw(screen)
        
        #update the display
        pygame.display.flip()
#DRAWING DONE ==========================================================================
    

def menu(screen):
    menuWin = createMenuWin()
    menu = True
    
    #keep showing the menu until the user decides to go elsewhere
    while (menu):
        for event in pygame.event.get():
            #if users quits, exit the game
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            #if the mouse was clicked, check if any buttons were clicked
            elif event.type == MOUSEBUTTONDOWN:
                clicked=menuWin.click(screen,event.pos)
                if(clicked):
                    #if the "play" button was clicked, exit the main menu and start the game
                    if(clicked==MENU_BTN_PLAY):
                        menu=False
                        break
                        
                    #if the instructions button was clicked, show the instructions window
                    elif (clicked==MENU_BTN_HOW):
                        print "Instructions!"
                    
                    #if the exit button was clicked, close the game
                    elif (clicked==MENU_BTN_EXIT):
                        pygame.quit()
                        sys.exit()
        
        #draw the background image & menu window
        screen.fill(Color(0,0,0))
        menuWin.draw(screen)
        
        pygame.display.flip() #update the display

#main program - sets up pygame & controls between-screen flow (mainmenu, game)
def main():
    #setup game screen
    gameScreen = pygame.display.set_mode(GAME_SIZE)
    
    #continue to loop through the menu & game until the program is exited
    while True:
        #start the menu
        menu(gameScreen)
    
        #start the game (if "play" was clicked in menu)
        game(gameScreen);

#Start program
if __name__ == "__main__":
    main()