from __future__ import print_function

import os
import random
from tilemap import Map, TiledMap, Camera, TileSet
import pygame as pg
vec = pg.math.Vector2
from sprites import *

def is_between(x, low, high):
    return x >= 0 and x <= high

def carve_maze(row, col, grid):
    N, S, E, W = 1, 2, 4, 8
    directions = [N, S, E, W]
    random.shuffle(directions)
    deltas = {N: (-1, 0),
              S: (1, 0),
              W: (0, -1),
              E: (0, 1)}
    reverse = {N: S, S: N, E: W, W: E}

    height = len(grid)
    width = len(grid[0])

    for dir in directions:
        new_r = row + deltas[dir][0]
        new_c = col + deltas[dir][1]

        if is_between(new_r, 0, height - 1) and \
           is_between(new_c, 0, width - 1) and \
           grid[new_r][new_c] == 0:
            grid[row][col] |= dir
            grid[new_r][new_c] |= reverse[dir]
            carve_maze(new_r, new_c, grid)
    

def generate_maze(height, width):
    maze = [[0 for c in range(width)]
            for r in range(height)]
    carve_maze(height // 2, width // 2, maze)
    return maze

def convert_to_thick_walls(maze):
    h_thin, w_thin = len(maze), len(maze[0])
    h = (2 * h_thin) + 1
    w = (2 * w_thin) + 1

    N, S, E, W = 1, 2, 4, 8

    new = [[0 for col in range(w)]
           for row in range(h)]
    for row in range(h):
        new[row][0] = 1
        new[row][-1] = 1

    for col in range(w):
        new[0][col] = 1
        new[-1][col] = 1

    for row in range(h_thin):
        for col in range(w_thin):
            cell = maze[row][col]
            if (cell & S) == 0:
                new[2 * (row + 1)][(2 * col) + 1] = 1
            if (cell & E) == 0:
                new[(2 * row) + 1][2 * (col + 1)] = 1

            new[2 * row][2 * col] = 1
                
    return new

class Level:
    def __init__(self, game):
        self.game = game
        self.map_folder = game.map_folder

    def new(self):
        pass

    def make_map_from_file(self, file):
        self.map = TiledMap(os.path.join(self.map_folder, file))
        self.game.map = self.map
        self.game.map_img = self.map.make_map()
        self.game.map_rect = self.game.map_img.get_rect()

    def clear_sprites(self):
        game = self.game
        game.camera = Camera(self.map.width, self.map.height)
        game.all_sprites = pg.sprite.LayeredUpdates()
        game.walls = pg.sprite.Group()
        game.mobs = pg.sprite.Group()
        game.items = pg.sprite.Group()

    def spawn_tmx_objects(self):        
        game = self.game
        for tile_object in self.map.tmxdata.objects:
            object_center = vec(tile_object.x + tile_object.width / 2,
                                tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                game.player = Player(game, object_center.x, object_center.y)
            if tile_object.name == 'wall':
                Obstacle(game,
                         tile_object.x,
                         tile_object.y,
                         tile_object.width,
                         tile_object.height)
            if tile_object.name == 'mob':
                Mob(game, object_center.x, object_center.y)

            if tile_object.name in ['apple']:
                Item(game, object_center, tile_object.name)

class LevelOne(Level):
    def make_map(self):
        self.make_map_from_file('level_1.tmx')

    def new(self):
        self.spawn_tmx_objects()

class LevelTwo(Level):
    def make_map(self):
        self.make_map_from_file('level_2.tmx')

    def new(self):
        self.spawn_tmx_objects()
 
class LevelThree(Level):
    def make_map(self):
        tileset_path = os.path.join(self.game.map_folder, 'RPGpack_sheet.png')
        tileset = TileSet(tileset_path, tilesize=32)
        grass_tile_ids = [41, 42, 43, 44, 81, 82, 83, 84]
        grass_tiles = [tileset[id] for id in grass_tile_ids]

        wall_tile_ids = [267, 268, 269, 270]
        wall_tiles = [tileset[id] for id in wall_tile_ids]

        W = 10
        H = 10
        map_data = generate_maze(H, W)
        map_data = convert_to_thick_walls(map_data)

        H = len(map_data)
        W = len(map_data[0])

        self.map = Map(W, H)
        self.game.map = self.map

        empty_cells = []
        wall_cells = []
        map_img = pg.Surface((self.map.width, self.map.height))
        for r in range(H):
            for c in range(W):
                if map_data[r][c] == 0:
                    tile = random.choice(grass_tiles)
                    empty_cells.append((r, c))
                else:
                    tile = random.choice(wall_tiles)
                    wall_cells.append((r, c))
 
                map_img.blit(tile, (c * TILESIZE,
                                    r * TILESIZE))

        self.player_init_pos = random.choice(empty_cells)
        self.goal_pos = random.choice(empty_cells)

        self.game.map_img = map_img
        self.game.map_rect = map_img.get_rect()
        self.wall_cells = wall_cells

    def new(self):
        game = self.game
        pos = self.player_init_pos
        x = pos[1] * TILESIZE + TILESIZE / 2
        y = pos[0] * TILESIZE + TILESIZE / 2
        game.player = Player(game, x, y)

        for coords in self.wall_cells:
            Obstacle(game,
                     coords[1] * TILESIZE,
                     coords[0] * TILESIZE,
                     TILESIZE,
                     TILESIZE)

        pos = self.goal_pos
        x = pos[1] * TILESIZE + TILESIZE / 2
        y = pos[0] * TILESIZE + TILESIZE / 2
        Item(game, vec(x, y), 'goal',
             pickable=False, bobbing=False)
