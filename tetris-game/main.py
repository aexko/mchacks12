import sys
import pygame as pg
from settings import FIELD_RES, FPS, FIELD_COLOR
from Tetris import Tetris

class TetrisApp:
    def __init__(self):
        self._initialize_pygame()
        self.screen = pg.display.set_mode(FIELD_RES)
        self.clock = pg.time.Clock()
        self.running = True
        self.Tetris = Tetris(self)

    def _initialize_pygame(self):
        pg.init()
        pg.display.set_caption('Tetris')

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit_game()

    def _update(self):
        self.clock.tick(FPS)
        self.Tetris.update()

    def _draw(self):
        self.screen.fill(FIELD_COLOR)
        pg.display.flip()

    def _quit_game(self):
        pg.quit()
        sys.exit()

if __name__ == '__main__':
    TetrisApp().run()
