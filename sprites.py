import pygame as pg
from settings import *
from tilemap import collide_hit_rect
import pytweening as tween
import math

from copy import deepcopy

vec = pg.math.Vector2

def collide_with_walls(sprite, group, direction):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if hits:
        if direction == 'x':
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if sprite.vel.x < 0:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
        if direction == 'y':
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
        return True
    return False

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center

        self.vel = vec(0, 0)
        self.rot = 0 # right
        self.rot_speed = 0
        self.pos = vec(x, y)

        self.inventory_size = INVENTORY_SIZE
        self.inventory = []
        self.last_drop = 0

        self.goal = None
        self.goal_mode = False
        self.angle_goal_mode = False


    def status(self):
        result = {}
        result['pos'] = deepcopy(self.rect.center)
        result['rot'] = deepcopy(self.rot)
        result['inventory'] = deepcopy(self.inventory)

        return result

    def get_keys(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_e]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_COMMA]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_o]:
            self.vel = vec(-PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            try:
                self.pick('anything')
            except:
                pass
        if keys[pg.K_b]:
            cur_time = pg.time.get_ticks()
            if cur_time - self.last_drop > DROP_INTERVAL:
                try:
                    self.drop(0)
                    self.last_drop = cur_time
                except:
                    pass

    def go_forward(self, distance):
        self.goal = self.pos + vec(TILESIZE * distance, 0).rotate(-self.rot)
        self.goal_mode = True
        self.should_respond = True

    def turn(self, angle):
        self.angle_goal = angle % 360
        self.angle_goal_mode = True
        self.should_respond = True

    def pick(self, item_name):
        if len(self.inventory) >= self.inventory_size:
            raise RuntimeError("Inventory full")
        hits = pg.sprite.spritecollide(self, self.game.items, False, collide_hit_rect)
        found = False
        for hit in hits:
            if item_name == 'anything' or hit.type == item_name:
                if hit.pickable:
                    self.inventory.append(hit.type)
                    hit.kill()
                    self.game.response_queue.put("OK")
                    found = True
                    break
        if not found:
            self.game.response_queue.put("Not found")
        self.game.ready_for_command = True

    def drop(self, inventory_number):
        if inventory_number < 0 or inventory_number >= len(self.inventory):
            raise RuntimeError("Inventory index out of bounds")
        item_name = self.inventory.pop(inventory_number)
        Item(self.game, vec(self.rect.centerx,
                            self.rect.centery), item_name)
        self.game.response_queue.put("Dropped {}".format(item_name))
        self.game.ready_for_command = True

    def follow_goal(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0

        to_goal = self.goal - self.pos
        goal_rot = (to_goal).angle_to(vec(1, 0))

        real_speed = ROBOT_SPEED * self.game.dt
        goal_dist_sq = to_goal.length_squared()
        if to_goal.length_squared() < real_speed**2:
            self.pos = self.goal
        else:
            self.rot = goal_rot
            self.vel = vec(ROBOT_SPEED, 0).rotate(-goal_rot)

    def follow_angle(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0

        to_goal = self.angle_goal - self.rot
        to_goal = (to_goal + 180) % 360 - 180

        if to_goal > 0:
            self.rot_speed = ROBOT_ROT_SPEED
        else:
            self.rot_speed = -ROBOT_ROT_SPEED

        if abs(self.rot_speed * self.game.dt) > abs(to_goal):
            self.rot_speed = 0
            self.rot = self.angle_goal

    def goal_reached(self):
        return self.pos == self.goal

    def angle_goal_reached(self):
        return self.rot == self.angle_goal

    def update(self):
        if self.goal_mode:
            self.follow_goal()
        elif self.angle_goal_mode:
            self.follow_angle()
        else:
            self.get_keys()

        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360

        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.hit_rect.center = self.pos

        self.pos += self.vel * self.game.dt 

        self.hit_rect.centerx = self.pos.x
        collided = collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collided = collide_with_walls(self, self.game.walls, 'y') or collided

        goal_reached = self.goal_reached()

        if self.goal_mode and collided and not goal_reached:
            self.game.response_queue.put("hit a wall")
            self.should_respond = False
            self.goal_mode = False
            self.game.ready_for_command = True

        if self.goal_mode and goal_reached:
            self.game.response_queue.put("goal reached")
            self.should_respond = False
            self.goal_mode = False
            self.game.ready_for_command = True

        if self.angle_goal_mode and self.angle_goal_reached():
            self.game.response_queue.put("angle goal reached")
            self.should_respond = False
            self.angle_goal_mode = False
            self.game.ready_for_command = True

        self.rect.center = self.hit_rect.center

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect

        self.pos = vec(x, y)
        self.rect.center = self.pos

        self.rot = 0

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))

        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y = self.y

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type, pickable=True, bobbing=True):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pickable = pickable

        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.bobbing = bobbing
        self.bob_step = 0
        self.bob_direction = 1

    def update(self):
        # bobbing
        if self.bobbing:
            offset = ITEM_BOB_RANGE * (self.tween(self.bob_step / ITEM_BOB_RANGE) - 0.5)
            self.rect.centery = self.pos.y + offset * self.bob_direction

            self.bob_step += ITEM_BOB_SPEED
            if self.bob_step > ITEM_BOB_RANGE:
                self.bob_step = 0
                self.bob_direction *= -1
