import random

from settings import *


class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, position):
        self.tetromino = tetromino
        self.position = vec(position) + INIT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        self.rect = self.image.get_rect()


    def is_alive(self):
        if not self.alive:
            self.kill()

    def set_rect_position(self):
        self.rect.topleft = self.position * TILE_SIZE

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True

    def rotate(self, pivot_pos):
        translated = self.position - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def update(self):
        self.set_rect_position()
        self.is_alive()


class Tetromino:
    def __init__(self, tetris):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, position) for position in TETROMINOES[self.shape]]
        self.landing = False


    def is_collide(self, block_positions):
        return any(map(Block.is_collide, self.blocks, block_positions))

    def rotate(self):
        pivot_pos = self.blocks[0].position
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.position = new_block_positions[i]

    def move(self, direction):
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.position + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.position += move_direction
        elif direction == 'DOWN':
            self.landing = True

    def update(self):
        self.move(direction='DOWN')
