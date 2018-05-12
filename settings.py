import os
import pygame as pg

WIDTH = 960 # 30 x 32
HEIGHT = 736 # 23 x 32

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
PLAYER_IMG = os.path.join('robot-pack', 'PNG', 'Top view', 'robot_3Dblue.png')
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0, 20, 20)

WALL_IMG = os.path.join('robot-pack', 'PNG', 'Top view', 'robot_3Dgreen.png')
