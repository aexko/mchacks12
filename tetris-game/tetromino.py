import random

from settings import *

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, position):
        self.tetromino = tetromino
        self.position = vec(position) + INIT_POS_OFFSET

        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position * TILE_SIZE

    def set_rect_position(self):
        self.rect.topleft = self.position * TILE_SIZE

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True



    # def is_collide(self, pos):
    #     x, y = int(pos.x), int(pos.y)
    #     if 0 <= x < FIELD_W and y < FIELD_H and (
    #             y < 0 or not self.tetromino.tetris.field_array[y][x]):
    #         return False
    #     return True

    def update(self):
        self.set_rect_position()
        self.is_collide(self.position)
        self.is_collide(self.position + MOVE_DIRECTIONS['DOWN'])


class Tetromino:
    def __init__(self, tetris):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
    #
    def is_collide(self, block_positions):
        return any(map(Block.is_collide, self.blocks, block_positions))


    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.position + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.position += move_direction


    def update(self):
        self.move(direction='DOWN')



