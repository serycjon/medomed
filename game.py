import pygame as pg
import argparse
import os
import sys

from queue import Queue
from threading import Thread
from time import sleep

from copy import deepcopy
import random

from tilemap import *
from settings import *
from sprites import *
from robot import *
import user_robots

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()  # for sound
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()
        self.command_queue = Queue()
        self.ready_for_command = True

    def load_img(self, path, size=None):
        img = pg.image.load(path).convert_alpha()
        if size is not None:
            img = pg.transform.scale(img, size)
        return img

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        assets_folder = os.path.join(game_folder, 'assets')
        map_folder = os.path.join(assets_folder, 'maps')
        img_folder = os.path.join(assets_folder, 'images')

        self.map = TiledMap(os.path.join(map_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.player_img = self.load_img(
            os.path.join(img_folder, PLAYER_IMG),
            (TILESIZE, TILESIZE))

        self.mob_img = self.load_img(
            os.path.join(img_folder, MOB_IMG),
            (TILESIZE, TILESIZE))

        self.wall_img = self.load_img(
            os.path.join(img_folder, WALL_IMG),
            (TILESIZE, TILESIZE))

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = \
                self.load_img(os.path.join(img_folder, ITEM_IMAGES[item]),
                              (TILESIZE, TILESIZE))

    def new(self):
        self.camera = Camera(self.map.width, self.map.height)
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.items = pg.sprite.Group()

        for tile_object in self.map.tmxdata.objects:
            object_center = vec(tile_object.x + tile_object.width / 2,
                                tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, object_center.x, object_center.y)
            if tile_object.name == 'wall':
                Obstacle(self,
                         tile_object.x,
                         tile_object.y,
                         tile_object.width,
                         tile_object.height)
            if tile_object.name == 'mob':
                Mob(self, object_center.x, object_center.y)

            if tile_object.name in ['apple']:
                Item(self, object_center, tile_object.name)

        self.draw_debug = False
        self.ready_for_command = True

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def menu(self):
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, LIGHTGREY, WIDTH/2, HEIGHT / 3)
        self.draw_text('Press any key to start...',
                       20,
                       LIGHTGREY,
                       WIDTH/2, HEIGHT / 3 + 60)
        pg.display.flip()
        self.wait_key()

    def wait_key(self):
        waiting = True
        while waiting:
            self.dt = self.clock.tick(FPS) / 1000.0

            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False
            
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
                if event.key == pg.K_d:
                    self.draw_debug = not self.draw_debug
        commands = {'forward': self.player.go_forward,
                    'turn': self.player.turn,
                    'status': self.status,
                    'pick': self.player.pick}
        if self.ready_for_command:
            try:
                command = self.command_queue.get(block=False)
                # print('command: {}'.format(command))
                if command[0] in commands:
                    self.ready_for_command = False
                    try:
                        commands[command[0]](*command[1:])
                    except Exception as e:
                        self.response_queue.put(repr(e))
                        self.ready_for_command = True
                else:
                    self.response_queue.put("incorrect command")
            except:
                pass

    def status(self):
        status = {}
        status['player'] = self.player.status()
        status['sense'] = {'on': [],
                           'near': []}
        for item in self.items:
            item_pos = item.rect.center
            to_item = item_pos - self.player.pos
            if to_item.length_squared() < ROBOT_SENSE_DIST**2:
                where = 'near'
                if pg.sprite.spritecollide(self.player, [item], False, collide_hit_rect):
                    where = 'on'
                status['sense'][where].append({'type': deepcopy(item.type),
                                               'vec': to_item})
        self.response_queue.put(status)
        self.ready_for_command = True

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        # Player hits item
        # hits = pg.sprite.spritecollide(self.player, self.items, False, collide_hit_rect)
        # for hit in hits:
        #     if hit.type == 'apple':
        #         pass

    def draw(self):
        pg.display.set_caption('fps: {:.2f}'.format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if hasattr(sprite, 'hit_rect'):
                rect = sprite.hit_rect
            else:
                rect = sprite.rect
            if self.draw_debug:
                pg.draw.rect(self.screen, WHITE,
                             self.camera.apply_rect(rect), 1)

        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, WHITE,
                             self.camera.apply_rect(wall.rect), 1)
            
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manual', action='store_true')
    parser.add_argument('--bot', help='robot class name', default='TestRobot')
    args = parser.parse_args()
    if not hasattr(user_robots, args.bot):
        print('robot not found!')
        sys.exit(1)

    game = Game()
    game.new()
    game.menu()
    if not args.manual:
        robot_class = getattr(user_robots, args.bot)
        print('robot_class: {}'.format(robot_class))

        robot = robot_class(game)
        robot.run()
    game.run()
