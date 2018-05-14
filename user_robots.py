from robot import Robot
from pprint import pprint
import pygame as pg
vec = pg.math.Vector2

class TestRobot(Robot):
    def worker(self):
        while True:
            status = self.status()
            pprint(status)
            self.sleep(2)
