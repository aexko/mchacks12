import cv2
import mediapipe as mp

# Initialisation de MediaPipe pour la détection de la main
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Fonction pour déterminer si la main est ouverte ou fermée
def is_hand_open(landmarks):
    # Vérification si les doigts sont ouverts
    thumb_open = landmarks[4].y < landmarks[3].y  # Pouce ouvert
    index_open = landmarks[8].y < landmarks[6].y  # Index ouvert
    middle_open = landmarks[12].y < landmarks[10].y  # Majeur ouvert
    ring_open = landmarks[16].y < landmarks[14].y  # Annulaire ouvert
    pinky_open = landmarks[20].y < landmarks[18].y  # Auriculaire ouvert

    # La main est ouverte si tous les doigts sont ouverts
    return thumb_open and index_open and middle_open and ring_open and pinky_open

# Fonction pour vérifier si le pouce et les autres doigts sont fermés
def is_thumb_and_other_fingers_closed(landmarks):
    thumb_closed = landmarks[4].y > landmarks[3].y  # Pouce fermé
    other_fingers_closed = (landmarks[8].y > landmarks[6].y and
                            landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y and
                            landmarks[20].y > landmarks[18].y)  # Index, majeur, annulaire et auriculaire fermés

    return thumb_closed and other_fingers_closed

# Fonction pour vérifier si la main est dans la configuration pour une rotation
def is_rotation_pose(landmarks):
    # Vérifier si uniquement le pouce et l'index sont ouverts
    thumb_open = landmarks[4].y < landmarks[3].y  # Pouce ouvert
    index_open = landmarks[8].y < landmarks[6].y  # Index ouvert
    other_fingers_closed = (landmarks[12].y > landmarks[10].y and
                            landmarks[16].y > landmarks[14].y and
                            landmarks[20].y > landmarks[18].y)  # Majeur, annulaire et auriculaire fermés

    # La rotation est possible si seul le pouce et l'index sont ouverts
    return thumb_open and index_open and other_fingers_closed

# Fonction pour déterminer la direction du "L"
def detect_L(landmarks, w, h):
    # Repères de l'index et du pouce
    index_finger_tip = landmarks[8]  # Point 8 : bout de l'index
    thumb_tip = landmarks[4]  # Point 4 : bout du pouce
    thumb_base = landmarks[1]  # Point 1 : base du pouce

    # Convertir les coordonnées normalisées en pixels
    index_x_pixel = int(index_finger_tip.x * w)
    index_y_pixel = int(index_finger_tip.y * h)

    # Vérifier si l'index est pointé vers le haut
    index_is_up = index_finger_tip.y < landmarks[6].y and index_finger_tip.x > landmarks[5].x  # Vérification simplifiée

    # Vérifier la direction du pouce (vers la gauche ou la droite)
    thumb_is_right = thumb_tip.x > thumb_base.x  # Si le tip du pouce est à droite de la base
    thumb_is_left = thumb_tip.x < thumb_base.x  # Si le tip du pouce est à gauche de la base

    # Retourner le résultat selon l'orientation de l'index et du pouce
    if index_is_up:
        if thumb_is_right:
            return "L vers la gauche", index_x_pixel, index_y_pixel
        elif thumb_is_left:
            return "L vers la droite", index_x_pixel, index_y_pixel
        else:
            return "Pouce pas assez orienté", index_x_pixel, index_y_pixel
    else:
        return "Index pas assez vertical", index_x_pixel, index_y_pixel

# Initialisation de la caméra
cap = cv2.VideoCapture(0)

# Définir la taille de la caméra
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)  # Largeur de l'image (400x400)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  # Hauteur de l'image (400x400)

# Variables pour suivre les mouvements
in_middle_block = False  # Si on est dans le bloc central
movement_done = False  # Si un déplacement a été effectué

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Conversion de l'image en RGB (MediaPipe attend une image RGB)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    # Dimensions de l'image
    h, w, _ = frame.shape
    
    # Calcul des positions des lignes verticales pour les blocs
    line_x_1 = int(w / 2 - w / 6)  # Ligne pour -1.5 sur X (gauche)
    line_x_2 = int(w / 2 + w / 6)  # Ligne pour +1.5 sur X (droite)
    
    # Tracer les lignes verticales (pour séparer les blocs)
    cv2.line(frame, (line_x_1, 0), (line_x_1, h), (255, 255, 255), 2)  # Ligne pour le bloc gauche
    cv2.line(frame, (line_x_2, 0), (line_x_2, h), (255, 255, 255), 2)  # Ligne pour le bloc droit
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Vérification si le pouce et les autres doigts sont fermés
            if is_thumb_and_other_fingers_closed(hand_landmarks.landmark):
                continue  # Ne rien faire si le pouce et les autres doigts sont fermés

            # Priorité à la détection de la rotation
            if is_rotation_pose(hand_landmarks.landmark):
                cv2.putText(frame, "Pose de rotation", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Détection de la main formant un "L"
                result, index_x_pixel, index_y_pixel = detect_L(hand_landmarks.landmark, w, h)
                # Afficher le résultat de la détection "L"
                cv2.putText(frame, result, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Dessin du bout de l'index (en bleu)
                cv2.circle(frame, (index_x_pixel, index_y_pixel), 10, (255, 0, 0), -1)
            
            # Vérification de la position de l'index pour le mouvement
            index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            
            # Convertir les coordonnées normalisées en pixels
            index_x_pixel = int(index_x * w)
            index_y_pixel = int(index_y * h)
            
            # Vérification de la position de l'index dans les blocs
            if line_x_1 < index_x_pixel < line_x_2:  # Dans le bloc central
                in_middle_block = True
                movement_done = False  # Réinitialiser le mouvement une fois dans le centre
                cv2.putText(frame, "Dans le centre", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            elif index_x_pixel < line_x_1:  # Bloc gauche
                if in_middle_block and not movement_done:
                    cv2.putText(frame, "Déplacement vers la gauche", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    movement_done = True  # Marquer que le mouvement a été effectué
                    in_middle_block = False  # L'index est hors du bloc central

            elif index_x_pixel > line_x_2:  # Bloc droit
                if in_middle_block and not movement_done:
                    cv2.putText(frame, "Déplacement vers la droite", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    movement_done = True  # Marquer que le mouvement a été effectué
                    in_middle_block = False  # L'index est hors du bloc central

            # Dessin des points de repère pour la main
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Affichage de l'image
    cv2.imshow("Hand Gesture Recognition", frame)
    
    # Sortie de la boucle si on appuie sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libération des ressources
cap.release()
cv2.destroyAllWindows()
