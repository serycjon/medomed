from robot import Robot
from time import sleep
from pprint import pprint
import pygame as pg
vec = pg.math.Vector2

class TestRobot(Robot):
    def worker(self):
        while True:
            status = self.status()
            pprint(status)
            sleep(2)

class ForwardRobot(Robot):
    def worker(self):
        while True:
            self.forward(1)
            sleep(2)
