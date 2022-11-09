import cv2
import mediapipe as mp
import matplotlib.pyplot as plt

from ProcessMpPose import *

#x,y,z
nao_joints =[[-0.022067232057452202, -0.021711817011237144, 0.4573521316051483, 0.009190082550048828, -0.05099792405962944, -0.1257903277873993], [-0.008456461131572723, 0.07549923658370972, 0.4317639172077179, 1.014843225479126, 1.3345519304275513, 0.9008655548095703], [-0.03297078236937523, -0.11895370483398438, 0.4300023019313812, -0.7951796054840088, 1.3543051481246948, -0.9337572455406189], [0.00828950759023428, 0.10938841849565506, 0.3326624631881714, -0.2028072327375412, 1.3345519304275513, 0.9008654952049255], [-0.021775726228952408, -0.15173956751823425, 0.3297538161277771, 0.5134648084640503, 1.3543051481246948, -0.9337572455406189], [0.0415092296898365, 0.10464451462030411, 0.28789252042770386, -1.0728727579116821, 0.9275916218757629, -0.14184515178203583], [0.009919078089296818, -0.15691250562667847, 0.28393805027008057, 1.3895469903945923, 0.9594386219978333, -0.1617850512266159], [-0.004878959618508816, 0.02834397554397583, 0.24658134579658508, -0.0024315807968378067, -0.15973584353923798, -0.01748642325401306], [-0.017386266961693764, -0.07086671143770218, 0.24568256735801697, 0.020527666434645653, -0.15777401626110077, -0.23618756234645844], [-0.007099629379808903, 0.0392739363014698, 0.14720518887043, 0.10980727523565292, -0.06824609637260437, -0.007283224258571863], [-0.020007099956274033, -0.07608125358819962, 0.1458529382944107, -0.05711428076028824, -0.0675090104341507, -0.24140648543834686], [-4.286970943212509e-05, 0.0504993200302124, 0.04516294598579407, 0.10955062508583069, 0.0001965649425983429, 0.0002566021867096424], [-0.0146822240203619, -0.08344155550003052, 0.04335466027259827, -0.056984517723321915, 0.004120092839002609, -0.24549849331378937]]

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode = True, min_detection_confidence = 0.3, model_complexity = 2)
mp_drawing = mp.solutions.drawing_utils

poseProcessor = MpPoseProcessorMath3D()

from frechetdist import frdist

def normalize(arr):

    max = -100000
    min = 100000
    for a in arr:
        for elem in a: 
            if elem > max:
                max = elem
            if elem < min:
                min = elem

    for i in range(len(arr)):
        for j in range(3): 
            arr[i][j] = (0.5-0) * (arr[i][j]-min)/(max-min) + 0.5

    return arr



def compare(nao,human):

    curve1 = [nao[1],nao[3],nao[5]]
    curve2 = [human[1],human[3],human[5]]

    t = ["x","y","z"]
    for i in range(len(curve1)):
        for j in range(i+1,len(curve1)):
            A = []
            B = []
            print(t[i],t[j])
            for z in range(len(curve1)):
                A.append([curve1[z][i],curve1[z][j]])
                B.append([curve2[z][i],curve2[z][j]])
            print(frdist(A,B))



import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8083))
msg = sock.recv(1024)
print(msg)
assert len(msg) > 0 and msg.decode('utf-8') == 'k'


def send_raw(msg):
    total = 0
    while total < len(msg):
        sent = sock.send(msg[total:])
        if sent == 0:
            return
        total += sent


def detectPose(image, pose, display = True, verbose = False):

    jointsNames = ["CABEZA","HOMBRO_IZQ","HOMBRO_DER","CODO_IZQ","CODO_DER","MUNECA_IZQ","MUNECA_DER","CINTURA_IZQ","CINTURA_DER","RODILLA_IZQ","RODILLA_DER","PIE_IZQ","PIE-DER"]
    joints = [0,11,12,13,14,15,16,23,24,25,26,27,28]


    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    height, width, _ = image.shape
    human_joints = []
    all_landmarks = []
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)


        for i,landmark in enumerate(results.pose_landmarks.landmark):
            # guardar todos los landmarks
            all_landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                  (landmark.z * width)))
            if i in joints:
                human_joints.append([landmark.x , landmark.y ,
                              landmark.z ])




    for i in range(len(human_joints)):
        aux = [-1 * human_joints[i][2], human_joints[i][0], -1 * human_joints[i][1]]
        human_joints[i] = aux

    # process pose, send to nao service and await for answer
    pose_dict = poseProcessor.get_pose_dict(all_landmarks)
    send_raw(json.dumps(pose_dict).encode('ascii'))
    raw_msg_in = sock.recv(4 * 1024)

    try:
        decoded = raw_msg_in.decode('utf-8')
        dic = json.loads(decoded)
        print(dic)
    except Exception as e:
        pass

    compare(normalize(nao_joints),normalize(human_joints))
    graphTest(nao_joints,human_joints)

    if display:
        plt.figure(figsize=[22,22])
        plt.plot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        plt.show()
        mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
        
    else:
        return output_image, human_joints

def graphTest(nao_joints,human_joints):
    fig = plt.figure()
    fig2 = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax2 = fig2.add_subplot(111,projection='3d')
    for a in nao_joints:
        ax.scatter(a[0], a[1], a[2])
    for b in human_joints:
        ax2.scatter(b[0], b[1], b[2])
    plt.show()

def webCamDisplay():
    
    # Configurar la función Pose para el vídeo.
    pose_video = mp_pose.Pose(static_image_mode = False, min_detection_confidence = 0.5, model_complexity = 1)

    # Inicializa el objeto VideoCapture para leer de la webcam.
    video = cv2.VideoCapture(0)

    # Crear una ventana con nombre para cambiar el tamaño
    cv2.namedWindow('Pose Detection in 3D', cv2.WINDOW_NORMAL)

    # Seteando las dimensiones de la camara
    video.set(3,1280)
    video.set(4,960)

    while video.isOpened():

        # Leer un frame
        ok, frame = video.read()

        # Si el frame no esta Ok
        if not ok:
            break
        
        # Voltea el marco horizontalmente para una visualización natural (selfie-view).
        frame = cv2.flip(frame, 1)

        # Obtener la anchura y la altura del frame
        frame_height, frame_width, _ =  frame.shape

        # Cambia el tamaño del cuadro manteniendo la relación de aspecto.
        frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

        # Realice la detección de puntos de referencia de la pose.
        frame, _ = detectPose(frame, pose_video, display = False)

        # Mostrar el frame
        cv2.imshow('Pose Detection in 3D', frame)

        # capturar que tecla se presiona
        k = cv2.waitKey(1) & 0xFF

        # si pulsa 'ESC' cerrar ventana
        if(k == 27):
            break

    # Liberar el objeto VideoCapture.
    video.release()

    # Cerrar la ventana
    cv2.destroyAllWindows()

image = cv2.imread('image.jpg')
detectPose(image, pose, display = True, verbose = False)




