from settings import *
import pygame as pg
from tetromino import Tetromino


from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft

class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'white',
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='LEFT')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='RIGHT')
        elif pressed_key == pg.K_UP:
            pass
        elif pressed_key == pg.K_DOWN:
            pass

    def update(self):
        if self.app.anim_trigger:
            self.tetromino.update()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)













