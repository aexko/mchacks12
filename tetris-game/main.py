import sys

import pygame as pg
import pathlib

from settings import FIELD_RES, FPS, FIELD_COLOR, ANIMATION_INTERVAL, BOOST_INTERVAL, SPRITE_DIR_PATH, TILE_SIZE
from tetris import Tetris


class TetrisApp:
    def __init__(self):
        self._initialize_pygame()
        self.screen = pg.display.set_mode(FIELD_RES)
        self.clock = pg.time.Clock()
        self.images = self.load_img()
        self.tetris = Tetris(self)
        self.set_timer()

    def _initialize_pygame(self):
        pg.init()
        pg.display.set_caption('Tetris')


    def load_img(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()

    def _handle_events(self):
        self.anim_trigger = False
        self.speed_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit_game()
            elif event.type == pg.KEYDOWN:
                self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.boost_event:
                self.speed_trigger = True

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.boost_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.boost_event = False
        pg.time.set_timer(self.user_event, ANIMATION_INTERVAL)
        pg.time.set_timer(self.boost_event, BOOST_INTERVAL)

    def _update(self):
        self.clock.tick(FPS)
        self.tetris.update()

    def _draw(self):
        self.screen.fill(FIELD_COLOR)
        self.tetris.draw()
        pg.display.flip()

    def _quit_game(self):
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    TetrisApp().run()
