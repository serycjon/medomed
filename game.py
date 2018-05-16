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
import levels

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
        self.draw_inventory = False

    def set_level(self, level_cls):
        self.level = level_cls(self)
        self.level.make_map()

    def load_img(self, path, size=None):
        img = pg.image.load(path).convert_alpha()
        if size is not None:
            img = pg.transform.scale(img, size)
        return img

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        self.game_folder = game_folder
        assets_folder = os.path.join(game_folder, 'assets')
        self.assets_folder = assets_folder
        map_folder = os.path.join(assets_folder, 'maps')
        self.map_folder = map_folder
        img_folder = os.path.join(assets_folder, 'images')
        self.img_folder = img_folder

        # self.map = TiledMap(os.path.join(map_folder, 'level_3.tmx'))
        # self.map_img = self.map.make_map()
        # self.map_rect = self.map_img.get_rect()

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
        self.level.clear_sprites()
        self.level.new()
        game.draw_debug = False
        game.ready_for_command = True

    def draw_text(self, text, size, color, x, y, align='midtop'):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'midtop':
            text_rect.midtop = (x, y)
        elif align == 'topleft':
            text_rect.topleft = (x, y)
        else:
            text_rect.bottomleft = (x, y)

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
                if event.key == pg.K_i:
                    self.draw_inventory = not self.draw_inventory

        commands = {'forward': self.player.go_forward,
                    'turn': self.player.turn,
                    'status': self.status,
                    'pick': self.player.pick,
                    'can_forward': self.player.can_go_forward,
                    'drop': self.player.drop}
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

        # draw inventory
        if self.draw_inventory:
            inv_height = TILESIZE
            inv_width = TILESIZE
            inv_in_margin = 5
            inv_out_margin = TILESIZE

            inv_len = self.player.inventory_size
            inv_H = inv_height
            inv_W = inv_len * inv_width + (inv_len - 1) * inv_in_margin
            inv_TL = (WIDTH - inv_W - inv_out_margin,
                      HEIGHT - inv_out_margin - inv_H)

            self.draw_text("INVENTORY", TILESIZE // 2, WHITE,
                           inv_TL[0], inv_TL[1],
                           align='bottomleft')
            inv_surf = pg.Surface((inv_W, inv_H))
            inv_surf.set_colorkey(BLACK)
            # inv_surf.fill(DARKGREY)

            for inv_place in range(inv_len):
                rect = pg.Rect(inv_place * (inv_width + inv_in_margin),
                               0,
                               inv_width,
                               inv_height)
                lw = 1
                if inv_place < len(self.player.inventory):
                    # pg.draw.rect(inv_surf,
                    #              LIGHTGREY,
                    #              rect, 0)
                    inv_surf.blit(self.item_images[self.player.inventory[inv_place]],
                                  rect)

                pg.draw.rect(inv_surf,
                             WHITE,
                             rect, 1)
            self.screen.blit(inv_surf, inv_TL)
            
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
    parser.add_argument('--level', help='level class name', default='LevelOne')
    args = parser.parse_args()
    if not hasattr(user_robots, args.bot):
        print('robot not found!')
        sys.exit(1)
    if not hasattr(levels, args.level):
        print('level not found!')
        sys.exit(1)

    game = Game()
    game.menu()
    if not args.manual:
        robot_class = getattr(user_robots, args.bot)
        robot = robot_class(game)
        robot.run()

    level_class = getattr(levels, args.level)
    game.set_level(level_class)
    game.new()
    game.run()
