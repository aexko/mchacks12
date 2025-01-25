from settings import *
import pygame as pg
from Tetromino import Tetromino

class Tetris:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.Tetromino = Tetromino(self)

    def update(self):
        self.Tetromino.update()

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                self._draw_tile(x, y)

    def _draw_tile(self, x, y):
        rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pg.draw.rect(self.screen, 'white', rect, 1)

    def draw(self):
        self.draw_grid()
