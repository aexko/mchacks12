from settings import *
from tetromino import Tetromino
from camera import *


class Tetris:
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self.boost = False

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
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def control(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='LEFT')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='RIGHT')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif is_index_down:
            self.boost = True

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
        self.sprite_group.update()

    def draw(self):
        # self.draw_grid()
        self.sprite_group.draw(self.app.screen)
