import pygame as pg
from pytmx.util_pygame import load_pygame
import pytmx

from settings import *

def collide_hit_rect(a, b):
    return a.hit_rect.colliderect(b.rect)

class Map:
    def __init__(self, width, height):
        self.layers = []
        self.layers.append([[None for col in range(width)] for row in range(height)])

        self.tilewidth = len(self.layers[0][0])
        self.tileheight = len(self.layers[0])

        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class TileSet:
    def __init__(self, filename, tilesize):
        self.tilesize = tilesize
        self.tileset = pg.image.load(filename).convert_alpha()
        self.width = self.tileset.get_size()[0] // self.tilesize

    def __getitem__(self, coords):
        if isinstance(coords, int):
            y = coords // self.width
            x = coords % self.width
        else:
            y, x = coords
        tile = pg.Surface((self.tilesize, self.tilesize))
        tileset_x = x * self.tilesize
        tileset_y = y * self.tilesize
        tile.blit(self.tileset, (0, 0),
                  (tileset_x, tileset_y,
                   self.tilesize, self.tilesize))
        return tile

class TiledMap:
    def __init__(self, filename):
        tm = load_pygame(filename, pixelaplha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid

        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)

                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        if self.width > WIDTH:
            x = min(x, 0)
            x = max(-(self.width - WIDTH), x)
        if self.height > HEIGHT:
            y = min(y, 0)
            y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(x, y, self.width, self.height)
