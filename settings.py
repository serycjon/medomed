import os
import pygame as pg

WIDTH = 960 # 30 x 32
HEIGHT = 736 # 23 x 32

FONT_NAME = 'arial'

TITLE = 'Medomed'
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (140, 140, 140)

BGCOLOR = DARKGREY

TILESIZE = 32
GRIDWITH = WIDTH / TILESIZE
DRIDHEIGHT = HEIGHT / TILESIZE

# Player
PLAYER_SPEED = 400
PLAYER_IMG = 'robot_3Dblue.png'
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0, 20, 20)
INVENTORY_SIZE = 3
DROP_INTERVAL = 500

WALL_IMG = 'robot_3Dred.png'

# Mobs
MOB_IMG = 'robot_3Dred.png'

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {'apple': 'apple.png',
               'goal': 'goal.png'}
ITEM_BOB_RANGE = 8
ITEM_BOB_SPEED = 0.2

# Robot
APPROACH_RADIUS = 20
ROBOT_ROT_SPEED = 60
ROBOT_SPEED = 100
ROBOT_SENSE_DIST = 150
