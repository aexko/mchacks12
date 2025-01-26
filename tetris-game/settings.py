import pygame as pg

vec = pg.math.Vector2

# FPS
FPS = 60

# BACKGROUND COLOR
FIELD_COLOR = (0, 0, 0)

TILE_SIZE = 50

# GRID SIZE
FIELD_SIZE = FIELD_W, FIELD_H = 10, 15
FIELD_RES = FIELD_W * TILE_SIZE, FIELD_H * TILE_SIZE

#
TETROMINOES = {
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'J': [(0, 0), (-1, 0), (1, 0), (1, -1)],
    'L': [(0, 0), (1, 0), (0, -1), (0, -2)],
    'I': [(0, 0), (0, 1), (0, -1), (0, -2)],
    'S': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'Z': [(0, 0), (1, 0), (0, -1), (-1, -1)]
}

# offset
INIT_POS_OFFSET = vec(FIELD_W // 2 - 1, 0)

MOVE_DIRECTIONS = {'LEFT': vec(-1, 0), 'RIGHT': vec(1, 0), 'DOWN': vec(0, 1)}

ANIMATION_INTERVAL = 400  # ms
BOOST_INTERVAL = 15  # ms

SPRITE_DIR_PATH = 'assets'
