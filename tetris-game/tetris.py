from settings import *
from tetromino import Tetromino
from camera import *
import pygame.freetype as ft


class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.boost = False
        self.score = 0
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 1000, 2: 3000, 3: 7000, 4: 15000}

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0

    # python
    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self.field_array[row][x] = self.field_array[y][x]

                if self.field_array[y][x]:
                    self.field_array[row][x].position = vec(x, y)

            if sum(map(bool, self.field_array[y])) < FIELD_W:
                row -= 1
            else:
                for x in range(FIELD_W):
                    self.field_array[row][x].alive = False
                    self.field_array[row][x] = 0

                self.full_lines += 1

    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x, y = int(block.position.x), int(block.position.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'white',
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE,
                              TILE_SIZE), 1)

    def check_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                self.__init__(self.app)
            else:
                self.boost = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def is_game_over(self):
        if self.tetromino.blocks[0].position.y == INIT_POS_OFFSET[1]:
            pg.time.wait(300)
            return True

    def update(self):
        trigger = [self.app.anim_trigger, self.app.speed_trigger][self.boost]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        # self.draw_grid()
        self.sprite_group.draw(self.app.screen)


class Text:
    def __init__(self, app):
        self.app = app
        self.font = ft.Font(FONT_PATH)

    def draw(self):
        print('score', self.app.tetris.score)
        self.font.render_to(self.app.screen, (WIN_W * 0.6, WIN_H * 0.21),
                            text='TETRAWAVE', fgcolor='white',
                            size=TILE_SIZE)
        self.font.render_to(self.app.screen, (WIN_W * 0.72, WIN_H * 0.55),
                            text='next', fgcolor='white',
                            size=TILE_SIZE)
        self.font.render_to(self.app.screen, (WIN_W * 0.705, WIN_H * 0.67),
                            text='score', fgcolor='white',
                            size=TILE_SIZE)
        self.font.render_to(self.app.screen, (WIN_W * 0.775, WIN_H * 0.8),
                            text=f'{self.app.tetris.score}',
                            fgcolor='white',
                            size=TILE_SIZE)
