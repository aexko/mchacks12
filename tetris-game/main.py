import pathlib
import sys
import time

import cv2
import mediapipe as mp

from settings import *
from tetris import Tetris
from camera import *



class TetrisApp:
    def __init__(self):
        self._initialize_pygame()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.images = self.load_img()
        self.tetris = Tetris(self)
        self.set_timer()

        # Vitesse de descente initiale
        self.drop_speed = 1000  # vitesse normale de descente
        self.min_drop_speed = 500  # vitesse minimale de descente
        self.acceleration_rate = 0.01
        self.last_drop_time = time.time()

        # Initialisation de la caméra
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

        # Variables pour suivre les mouvements
        self.in_middle_block = False
        self.movement_done = False
        self.left_block_time = 0
        self.right_block_time = 0
        self.translation_delay = 0.5  # Delay for translation (seconds)

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        pg.time.set_timer(self.user_event, ANIMATION_INTERVAL)

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

        # Gérer la descente du bloc
        current_time = time.time()
        if current_time - self.last_drop_time >= self.drop_speed:
            self.tetris.tetromino.move(direction='DOWN')
            self.last_drop_time = current_time

            # Accélérer la descente
            if self.drop_speed > self.min_drop_speed:
                self.drop_speed -= self.acceleration_rate

        self.tetris.update()

    def _draw(self):
        self.screen.fill(color=BACKGROUND_COLOR)
        self.screen.fill(color=FIELD_COLOR, rect=(0, 0, *FIELD_RES))
        self.tetris.draw()
        pg.display.flip()

    def _quit_game(self):
        pg.quit()
        sys.exit()

    def detect_gestures(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        h, w, _ = frame.shape
        line_x_1 = int(w / 2 - w / 6)
        line_x_2 = int(w / 2 + w / 6)

        cv2.line(frame, (line_x_1, 0), (line_x_1, h), (255, 255, 255), 2)
        cv2.line(frame, (line_x_2, 0), (line_x_2, h), (255, 255, 255), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if is_thumb_and_other_fingers_closed(hand_landmarks.landmark):
                    continue

                thumb_open = hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y
                if thumb_open and is_rotation_pose(hand_landmarks.landmark):
                    result, index_x_pixel, index_y_pixel = detect_L(hand_landmarks.landmark, w, h)
                    if result == "L vers la droite":
                        cv2.putText(frame, "Rotation droite", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                index_x_pixel = int(index_x * w)
                index_y_pixel = int(index_y * h)

                # Fonctionnalité de descente
                if is_fist(hand_landmarks.landmark):  # Poing fermé
                    cv2.putText(frame, "Descente complète", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.tetris.tetromino.move(direction='DOWN', full_drop=True)  # Descente immédiate

                elif is_index_down(hand_landmarks.landmark):  # Index vers le bas
                    cv2.putText(frame, "Descente d'un bloc", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.tetris.tetromino.move(direction='DOWN')  # Descente d'un bloc

                # Détection des mouvements gauche/droite
                if line_x_1 < index_x_pixel < line_x_2:
                    self.in_middle_block = True
                    self.movement_done = False
                    cv2.putText(frame, "Dans le centre", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                elif index_x_pixel < line_x_1:
                    self.right_block_time = time.time()
                    if self.in_middle_block and not self.movement_done:
                        cv2.putText(frame, "Déplacement vers la droite", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (255, 0, 0), 2)
                        self.movement_done = True
                        self.in_middle_block = False

                elif index_x_pixel > line_x_2:
                    self.left_block_time = time.time()
                    if self.in_middle_block and not self.movement_done:
                        cv2.putText(frame, "Déplacement vers la gauche", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 2)
                        self.movement_done = True
                        self.in_middle_block = False

                # Translation check based on time spent in the left or right block
                if time.time() - self.left_block_time >= self.translation_delay:
                    self.tetris.tetromino.move(direction='LEFT')
                    self.left_block_time = time.time()

                if time.time() - self.right_block_time >= self.translation_delay:
                    self.tetris.tetromino.move(direction='RIGHT')
                    self.right_block_time = time.time()

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Gesture Recognition", frame)

    def run(self):
        while True:
            self._handle_events()
            self._update()
            self.detect_gestures()
            self._draw()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    TetrisApp().run()
