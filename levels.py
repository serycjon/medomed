from __future__ import print_function

import os
from tilemap import TiledMap, Camera
import pygame as pg
vec = pg.math.Vector2
from sprites import *

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
        self.make_map_from_file('level_3.tmx')

    def new(self):
        self.spawn_tmx_objects()
