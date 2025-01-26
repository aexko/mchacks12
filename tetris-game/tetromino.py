import random
import pygame as pg
from settings import *  # Assurez-vous que les constantes comme TILE_SIZE, FIELD_W, FIELD_H sont bien définies dans settings.py

# Liste des couleurs possibles pour les formes de tétromino
BLOCK_COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'L': 'orange',
    'J': 'blue',
    'S': 'green',
    'Z': 'red',
}

class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, position, color):
        self.tetromino = tetromino
        self.position = vec(position) + INIT_POS_OFFSET
        self.alive = True

        # Utiliser la couleur du tétromino (passée en paramètre)
        self.color = color

        super().__init__(tetromino.tetris.sprite_group)
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(self.color)  # Appliquer la couleur choisie au bloc
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position * TILE_SIZE

    def set_rect_position(self):
        self.rect.topleft = self.position * TILE_SIZE

    def is_collide(self, pos):
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True

    def rotate(self, pivot_pos):
        translated = self.position - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def update(self):
        self.set_rect_position()
        self.is_collide(self.position)
        self.is_collide(self.position + MOVE_DIRECTIONS['DOWN'])

class Tetromino:
    def __init__(self, tetris):
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))  # Choisir une forme aléatoire
        
        # Choisir une couleur unique pour la forme
        self.color = BLOCK_COLORS[self.shape]  # Récupérer la couleur pour cette forme spécifique
        
        # Créer des blocs avec la même couleur pour tout le tétromino
        self.blocks = [Block(self, pos, self.color) for pos in TETROMINOES[self.shape]]
        
        self.landing = False

        # Délai de mouvement et variables d'accélération
        self.move_delay = 1000  # Temps en millisecondes (1 seconde)
        self.min_move_delay = 100  # Délai minimum (vitesse maximale)
        self.acceleration = 10  # L'accélération, diminue le délai à chaque mouvement

        self.last_move_time = pg.time.get_ticks()  # Temps du dernier mouvement

    def is_collide(self, block_positions):
        # Vérifier s'il y a une collision avec l'emplacement des blocs
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
        current_time = pg.time.get_ticks()

        # Vérifier si le délai est écoulé avant de déplacer le bloc vers le bas
        if current_time - self.last_move_time >= self.move_delay:
            # Effectuer le mouvement vers le bas
            self.move(direction='DOWN')
            self.last_move_time = current_time  # Mettre à jour le temps du dernier mouvement

            # Accélérer la descente (réduire le délai entre les mouvements)
            if self.move_delay > self.min_move_delay:
                self.move_delay -= self.acceleration  # Réduire le délai pour augmenter la vitesse
            else:
                self.move_delay = self.min_move_delay  # Ne pas descendre plus vite que la vitesse minimale
