import mediapipe as mp


# Initialisation de MediaPipe pour la détection de la main
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Fonction pour déterminer si la main est ouverte ou fermée
def is_hand_open(landmarks):
    thumb_open = landmarks[4].y < landmarks[3].y
    index_open = landmarks[8].y < landmarks[6].y
    middle_open = landmarks[12].y < landmarks[10].y
    ring_open = landmarks[16].y < landmarks[14].y
    pinky_open = landmarks[20].y < landmarks[18].y
    return thumb_open and index_open and middle_open and ring_open and pinky_open


# Fonction pour vérifier si le pouce et les autres doigts sont fermés
def is_thumb_and_other_fingers_closed(landmarks):
    thumb_closed = landmarks[4].y > landmarks[3].y
    other_fingers_closed = (landmarks[8].y > landmarks[6].y and
                            landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y and
                            landmarks[20].y > landmarks[18].y)
    return thumb_closed and other_fingers_closed


# Fonction pour vérifier si la main est dans la configuration pour une rotation
def is_rotation_pose(landmarks):
    thumb_open = landmarks[4].y < landmarks[3].y
    index_open = landmarks[8].y < landmarks[6].y
    other_fingers_closed = (landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y and
                            landmarks[20].y > landmarks[18].y)
    return thumb_open and index_open and other_fingers_closed


# Fonction pour détecter l'index vers le bas
def is_index_down(landmarks):
    return landmarks[8].y > landmarks[6].y


# Fonction pour détecter un poing fermé
def is_fist(landmarks):
    # Si tous les doigts sont fermés, on considère que c'est un poing
    return is_thumb_and_other_fingers_closed(landmarks)


# Fonction pour déterminer la direction du "L"
def detect_L(landmarks, w, h):
    index_finger_tip = landmarks[8]
    thumb_tip = landmarks[4]
    thumb_base = landmarks[1]
    index_x_pixel = int(index_finger_tip.x * w)
    index_y_pixel = int(index_finger_tip.y * h)
    index_is_up = index_finger_tip.y < landmarks[6].y and index_finger_tip.x > landmarks[5].x
    thumb_is_right = thumb_tip.x > thumb_base.x
    thumb_is_left = thumb_tip.x < thumb_base.x
    if index_is_up:
        if thumb_is_right:
            return "L vers la gauche", index_x_pixel, index_y_pixel
        elif thumb_is_left:
            return "L vers la droite", index_x_pixel, index_y_pixel
        else:
            return "Pouce pas assez orienté", index_x_pixel, index_y_pixel
    else:
        return "Index pas assez vertical", index_x_pixel, index_y_pixel
