#Filename: gameConstants.py
#Author: Ryan Blakely
#Last Modified By: Ryan Blakely
#Last Modified: July 15th, 2013
#Description: Constants required for the ZombieMiner.py game

import pygame
from pygame.locals import *

#width,height in position tuples, etc etc...
X=0
Y=1

#direction constants...
DIR_RIGHT=0
DIR_LEFT=1
DIR_UP=2
DIR_DOWN=3

#action constants
ACT_NONE=0
ACT_WALK=1
ACT_DIG=2

#general constants
SCREEN_SIZE=(500,500)
FLIPVAL="^"
WIN_POS=(48,48) #winning tile position

#map constants
MAP_SIZE=(50,50)
MAP_FILE = "above.txt"
MAP_FILE_DLIM='\t'

#tile constants
TILE_TRANSCOLOR = Color(255,0,255)
TILE_SIZE=(48,48)

#image file locations
IMG_DIR = 'images/'
IMG_ZOMBIE=IMG_DIR+'zombie.png'
IMG_PLAYER=IMG_DIR+'player.png'
IMG_CRACKS=IMG_DIR+'cracks.png'
IMG_TILESET=IMG_DIR+'mines.png'
IMG_FIRE=IMG_DIR+'fire.png'
IMG_BTNSET=IMG_DIR+'buttonset.png'
IMG_WINSET=IMG_DIR+'winset.png'
IMG_MENUBG=IMG_DIR+"menuBg.png"


#spriteset template (RL) for both player and zombiea
SPRITE_SIZE = TILE_SIZE #currently, changing this might mess things up
SPRITE_TEMPLATE=[[['0'],['^0']], #standing
                [['0','1','2','3'],['^0','^1','^2','^3']], #walking
                [['4','5','6','7'],['^4','^5','^6','^7']]] #axing
FIRE_TEMPLATE=[[['0','1','2','^1','3','^2','0','3','2']]] #uses a template/spriteset so it can have duplicates of frames 
#sprite animation delay "bases"
SPRITE_FRAME_DELAY = 800 #delay between frames
SPRITE_ACT_DELAY = 400 #delay between acts
SPRITE_MASK_DELAY = 200 #delay between mask ani frames

#miner statistic constants
STAT_SP='sp' #players speed
STAT_STR='str' #players strength 
STAT_MAXBAG='maxBag' #the current maximum bag size
STAT_MONEY='money' #the pplayers money 
STAT_BAG = 'bag' #players current bag (list)
STAT_ORIGINAL_BAG='origBag' #the original bag size assigned to the player at game runtime

#player constants
PLAYER_STATS = {STAT_SP:1,STAT_STR:1,STAT_MAXBAG:4,STAT_MONEY:0} #player initial stats
PLAYER_STARTPOS = (4,4) #players initial position

#zombie constants
ZOMBIE_NUM=10 #number of zombies
ZOMBIE_STR=0.01 #zombie base str
ZOMBIE_SP=0.03 #zombie base sp

#special mines (tiles)
MINE_DUG = 21
MINE_ROCK=0
MINE_BLANK=1
MINE_WIN=17

#types of mines
MINE_BLOCK_FULL=2
MINE_BLOCK_UP=1
MINE_BLOCK_NONE = 0
MINE_DIGGABLE = 4 #just for readability
MINE_SHOP=3

MINE_VAL_WIN=-1 #special winning mine value

#all of the available "mines" (tiles) in the game, and their associated properties
mines={ #diggable tiles - first is blank, last is win, others are minable
        MINE_BLANK: {'chance':80,'value':0,'type':MINE_DIGGABLE,'hits':5},
        2:          {'chance':22,'value':1,'type':MINE_DIGGABLE,'hits':7},
        3:          {'chance':17,'value':2,'type':MINE_DIGGABLE,'hits':9},
        4:          {'chance':15,'value':3,'type':MINE_DIGGABLE,'hits':10},
        5:          {'chance':14,'value':4,'type':MINE_DIGGABLE,'hits':13},
        6:          {'chance':12,'value':5,'type':MINE_DIGGABLE,'hits':15},
        7:          {'chance':10,'value':6,'type':MINE_DIGGABLE,'hits':20},
        8:          {'chance':9,'value':7,'type':MINE_DIGGABLE,'hits':22},
        9:          {'chance':8,'value':8,'type':MINE_DIGGABLE,'hits':25},
        10:         {'chance':7,'value':9,'type':MINE_DIGGABLE,'hits':30},
        11:         {'chance':6,'value':10,'type':MINE_DIGGABLE,'hits':32},
        12:         {'chance':5,'value':11,'type':MINE_DIGGABLE,'hits':35},
        13:         {'chance':4,'value':12,'type':MINE_DIGGABLE,'hits':48},
        14:         {'chance':3,'value':13,'type':MINE_DIGGABLE,'hits':55},
        15:         {'chance':2,'value':14,'type':MINE_DIGGABLE,'hits':65},
        16:         {'chance':1,'value':15,'type':MINE_DIGGABLE,'hits':75},
        MINE_WIN:   {'chance':0,'value':MINE_VAL_WIN,'type':MINE_DIGGABLE,'hits':100},
        
        #misc tiles
        MINE_ROCK:  {'chance':18,'value':0,'type':MINE_BLOCK_FULL}, #rock
        18:         {'chance':0,'value':0,'type':MINE_BLOCK_UP,}, #outside tile
        19:         {'chance':0,'value':0,'type':MINE_BLOCK_FULL}, #cave-outside (side)
        20:         {'chance':0,'value':0,'type':MINE_BLOCK_FULL}, #cave-outside (bottom)
        MINE_DUG:   {'chance':0,'value':0,'type':MINE_BLOCK_NONE}, #dug out tile
            
        #house tiles (roof x3, then floor x3)
        22:         {'chance':0,'value':0,'type':MINE_BLOCK_UP},
        23:         {'chance':0,'value':0,'type':MINE_BLOCK_UP},
        24:         {'chance':0,'value':0,'type':MINE_BLOCK_UP},
        
        25:         {'chance':0,'value':0,'type':MINE_SHOP},
        26:         {'chance':0,'value':0,'type':MINE_SHOP},
        27:         {'chance':0,'value':0,'type':MINE_SHOP},               
      }

#order the AI will check in order to choose which direction to move in
AI_CHECKORDER = {DIR_UP:    [DIR_UP,DIR_RIGHT,DIR_LEFT,DIR_DOWN],
                 DIR_RIGHT: [DIR_RIGHT,DIR_UP,DIR_DOWN,DIR_LEFT],
                 DIR_LEFT:  [DIR_LEFT,DIR_UP,DIR_DOWN,DIR_RIGHT],
                 DIR_DOWN:  [DIR_DOWN,DIR_RIGHT,DIR_LEFT,DIR_UP]}


#special window position constants
ALIGN_CENTER=-1 #position value used for window-UI centering
ALIGN_BOTTOM=-2 #position value used for window-UI bottom-alignment

#font constants for UI
WIN_TITLE_FONT = 45
WIN_FONT_SIZE = 30
WIN_FONT_SMALL_SIZE = 18
WIN_FONT_COLOR = pygame.Color(150,100,75) #brownish
WIN_FONT_FILE = "ButterflyKids.ttf"

#create fonts for the windows
WIN_TITLE_FONT = pygame.font.Font(WIN_FONT_FILE,WIN_TITLE_FONT)
WIN_FONT = pygame.font.Font(WIN_FONT_FILE,WIN_FONT_SIZE)
WIN_FONT_SMALL = pygame.font.Font(WIN_FONT_FILE,WIN_FONT_SMALL_SIZE)
BTN_FONT = pygame.font.Font(WIN_FONT_FILE,WIN_FONT_SMALL_SIZE)

#window image sets ui order
WINSET_IMG_TOP=0 
WINSET_IMG_BTM=2
WINSET_IMG_PNL=1

#button image sets ui order
BTNSET_IMG_LEFT=0
BTNSET_IMG_RIGHT=2
BTNSET_IMG_MID=1

#shop constants
SHOP_COST_STR=20 #cost of str
SHOP_COST_SP=20 #cost of sp
SHOP_BTN_TEXT="buy" #button text for shop buttons
SHOP_TITLE="Ye Olde Shop" #title for the shop
SHOP_BTN_STR="shopStr" #id for buy str button
SHOP_BTN_SP="shopSp" #id for buy sp button
#label text for the shop items
SHOP_LABELS=["Strength  $"+str(SHOP_COST_STR),
             "Speed     $"+str(SHOP_COST_SP)]

#menu buttons - button id's and button text
MENU_BTN_PLAY = "Play"
MENU_BTN_HOW = "Instructions"
MENU_BTN_EXIT = "Exit"
MENU_BTN = "Return to Menu"
MENU_TITLE = "Main Menu"