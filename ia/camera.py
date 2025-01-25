import cv2
import mediapipe as mp

# Initialisation de MediaPipe pour la détection de la main
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

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
            return "L vers la droite", index_x_pixel, index_y_pixel
        elif thumb_is_left:
            return "L vers la gauche", index_x_pixel, index_y_pixel
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

# Boucle principale
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
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
                # Détection de la main formant un "L"
                result, index_x_pixel, index_y_pixel = detect_L(hand_landmarks.landmark, w, h)
                
                # Afficher le résultat de la détection "L"
                cv2.putText(frame, result, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Dessin du bout de l'index (en bleu)
                cv2.circle(frame, (index_x_pixel, index_y_pixel), 10, (255, 0, 0), -1)
                
                # Vérification de la position de l'index dans les blocs
                if line_x_1 < index_x_pixel < line_x_2:  # Dans le bloc central
                    in_middle_block = True
                    movement_done = False  # Réinitialiser le mouvement une fois dans le centre
                    cv2.putText(frame, "Dans le centre", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                elif index_x_pixel < line_x_1:  # Bloc gauche
                    if in_middle_block and not movement_done:
                        cv2.putText(frame, "Déplacement vers la gauche", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        movement_done = True  # Marquer que le mouvement a été effectué
                        in_middle_block = False  # L'index est hors du bloc central

                elif index_x_pixel > line_x_2:  # Bloc droit
                    if in_middle_block and not movement_done:
                        cv2.putText(frame, "Déplacement vers la droite", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        movement_done = True  # Marquer que le mouvement a été effectué
                        in_middle_block = False  # L'index est hors du bloc central

                # Dessin des points de repère
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Affichage de l'image
        cv2.imshow("Tracking Index Finger with Blocks and L", frame)
        
        # Sortie de la boucle si on appuie sur 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Libération des ressources
cap.release()
cv2.destroyAllWindows()
