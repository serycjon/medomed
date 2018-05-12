import pygame as pg
import os
import sys

from tilemap import *
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()  # for sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_img(self, path, size=None):
        img = pg.image.load(path).convert_alpha()
        if size is not None:
            img = pg.transform.scale(img, size)
        return img

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        assets_folder = os.path.join(game_folder, 'assets')
        map_folder = os.path.join(assets_folder, 'maps')

        self.map = TiledMap(os.path.join(map_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.player_img = self.load_img(
            os.path.join(assets_folder, PLAYER_IMG),
            (TILESIZE, TILESIZE))

        self.mob_img = self.load_img(
            os.path.join(assets_folder, MOB_IMG),
            (TILESIZE, TILESIZE))

        self.wall_img = self.load_img(
            os.path.join(assets_folder, WALL_IMG),
            (TILESIZE, TILESIZE))

    def new(self):
        self.camera = Camera(self.map.width, self.map.height)
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()

        # for r, tiles in enumerate(self.map.data):
        #     for c, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, c, r)
        #         if tile == 'P':
        #             self.player = Player(self, c, r)
        #         if tile == 'M':
        #             Mob(self, c, r)
        self.player = Player(self, 5, 5)

    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit(0)

    def events(self):
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        pg.display.set_caption('fps: {:.2f}'.format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))
        

if __name__ == '__main__':
    game = Game()
    game.new()
    game.run()

