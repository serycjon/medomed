import pygame as pg

from settings import *

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'r') as fin:
            for line in fin:
                self.data.append(line)

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)

        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

        
