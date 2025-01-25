import cv2
import mediapipe as mp

# Initialisation de MediaPipe pour la détection de la main
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

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
    
    # Traitement de l'image pour détecter les mains
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
            # Coordonnée du bout de l'index (point 8)
            index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            
            # Convertir les coordonnées normalisées en pixels
            index_x_pixel = int(index_x * w)
            index_y_pixel = int(index_y * h)
            
            # Dessiner le bout de l'index (en bleu)
            cv2.circle(frame, (index_x_pixel, index_y_pixel), 10, (255, 0, 0), -1)
            
            # Vérification de la position de l'index dans les blocs
            if line_x_1 < index_x_pixel < line_x_2:  # Dans le bloc central
                in_middle_block = True
                movement_done = False  # Réinitialiser le mouvement une fois dans le centre
                cv2.putText(frame, "Dans le centre", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
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

    # Affichage de l'image
    cv2.imshow("Tracking Index Finger with Blocks", frame)
    
    # Sortie de la boucle si on appuie sur 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libération des ressources
cap.release()
cv2.destroyAllWindows()
