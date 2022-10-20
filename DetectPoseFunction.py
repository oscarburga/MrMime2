import math
import cv2
import numpy as np
from time import time
import mediapipe as mp
import matplotlib.pyplot as plt

# Inicializando la clase de pose de mediapipe
mp_pose = mp.solutions.pose

# Seteando la funcion 'Pose'
pose = mp_pose.Pose(static_image_mode = True, min_detection_confidence = 0.3, model_complexity = 2)

# Inicialización de la clase de dibujo mediapipe, útil para la anotación.
mp_drawing = mp.solutions.drawing_utils 

def detectPose(image, pose, display = True, verbose = False):
    '''
    Esta función realiza la detección de la postura en una imagen.
    Args:
        Imagen: La imagen de entrada con una persona destacada cuyos puntos de referencia de pose necesitan ser detectados.
        pose: La función de configuración de la pose necesaria para realizar la detección de la misma.
        display: Un valor booleano que si se establece en true la función muestra la imagen resultante 
                 y los puntos de referencia de la pose en un gráfico 3D y no devuelve nada.
        Verbose: Un valor booleano que si se establece en true Mostra los landmarks en consola de todos los puntos (33 en total)

    Devuelve:
        imagen_salida: La imagen de entrada con los puntos de referencia de pose detectados dibujados.
        puntos de referencia: Una lista de puntos de referencia detectados convertidos a su escala original.

    '''
    
    # Crea una copia de la imagen de entrada
    output_image = image.copy()
    
    # Convertir la imagen de BGR a RGB
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Realiza la deteccion de poses
    results = pose.process(imageRGB)
    
    # Extrae el height y width de la imagen de entrada
    height, width, _ = image.shape
    
    # Inicializamos la lista donde almacenaremos los puntos de referencia
    landmarks = []
    
    if results.pose_world_landmarks:
    
        # Dibuja los puntos de referencia de la pose en la imagen de salida.
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)
        
        # Iteramos por todos los puntos de referencia detectados
        for landmark in results.pose_world_landmarks.landmark:
    
            # Añadimos los puntos de referencia a la lista
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                              (landmark.z * width)))

    if verbose:
        print('Landmarks are: ', landmarks)
    
    # Comprueba si la imagen de entrada y la imagen resultante están especificadas para ser mostradas.
    if display:
    
        # Muestra la imagen de entrada y la imagen resultante.
        plt.figure(figsize=[22,22])
        plt.plot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        
        # También traza los puntos de referencia de la Pose en 3D.
        mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
        
    else:
        
        return output_image, landmarks

