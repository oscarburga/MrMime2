from matplotlib import image
from naoqi import ALProxy
import matplotlib.pyplot as plt
import numpy as np
import math
import Tkinter as tk
from PIL import ImageTk, Image
import tkFileDialog as filedialog
import imutils
import cv2 as cv

class Vector:
    X1 = 0
    Y1 = 0
    X2 = 0
    Y2 = 0
    vector = np.array([0,0])
    def __init__(self, X1, Y1, X2, Y2):
        self.isOk = True
        if any([True if val is None else False for val in (X1, Y1, X2, Y2)]):
            self.isOk = False
            self.X1 = .0
            self.Y1 = .0
            self.X2 = .0
            self.Y2 = .0
            return
        self.X1 = X1
        self.Y1 = Y1
        self.X2 = X2
        self.Y2 = Y2
        self.vector = np.array([X2-X1,Y2-Y1])

def product_point(p,q):
    return np.dot(p,q)

def producto_cross(p,q):
    return np.cross(p,q)

def angle(p,q):
    return math.atan2(producto_cross(p,q), product_point(p,q))

###########################################################################################

net=cv.dnn.readNetFromTensorflow("graph_opt.pb")## weigths

NAO_HOST = "127.0.0.1"
NAO_PORT = 9559
Motion = ALProxy("ALMotion", NAO_HOST, NAO_PORT)
Speech = ALProxy("ALTextToSpeech", NAO_HOST, NAO_PORT)
#names = ['LElbowRoll', 'LShoulderRoll', 'LShoulderPitch']
names = ['RElbowRoll', 'RShoulderRoll', 'LElbowRoll', 'LShoulderRoll','RElbowYaw','LElbowYaw']
#times = [[1.0], [1.2], [1.3]]
times = [[1.0], [1.2],[1.0], [1.2],[1.0], [1.2]]
inWidth=368
inHeight=368
thr=0.2
points=[]
flag = 0

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                ["Neck", "RHip"], ["Neck", "LHip"] ]

def pose_estimation(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out=out[:, :19, :, :]
    
    assert(len(BODY_PARTS) <= out.shape[1])
    global points 
    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
    t, _ = net.getPerfProfile()
    freq = cv.getTickFrequency() / 1000
    cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
    return frame, points

def getAnglesFromPoints(points):
    xs=[]
    ys=[]
    for i, pos in enumerate(points):
        if i == 2 or i == 3 or i == 4 or i==5 or i==6 or i==7 or i==8 or i==11:
            xs.append(None if pos is None else pos[0])
            ys.append(None if pos is None else pos[1])
    print(points)
    print(xs)
    print(ys)

    #RElbowRoll and RShoulderRoll
    PRElbow=Vector(xs[1],ys[1],xs[0],ys[0])
    QRElbow=Vector(xs[1],ys[1],xs[2],ys[2])
    PRShoulder=Vector(xs[0],ys[0],xs[6],ys[6])
    QRShoulder=Vector(xs[0],ys[0],xs[1],ys[1])

    #LElbowRoll and lShoulderRoll
    PLElbow=Vector(xs[4],ys[4],xs[3],ys[3])
    QLElbow=Vector(xs[4],ys[4],xs[5],ys[5])
    PLShoulder=Vector(xs[3],ys[3],xs[7],ys[7])
    QLShoulder=Vector(xs[3],ys[3],xs[4],ys[4])

    #Variables
    RElbowRoll = None
    LElbowRoll = None
    RShoulderRoll = None
    LShoulderRoll = None

    if PRElbow.isOk and QRElbow.isOk:
        RElbowRoll=angle(PRElbow.vector, QRElbow.vector)

    if PLElbow.isOk and QLElbow.isOk:
        LElbowRoll=angle(PLElbow.vector, QLElbow.vector)

    if PRShoulder.isOk and QRShoulder.isOk:
        RShoulderRoll = angle(PRShoulder.vector, QRShoulder.vector)

    if PLShoulder.isOk and QLShoulder.isOk:
        LShoulderRoll = angle(PLShoulder.vector, QLShoulder.vector)

    def addMindNone(x, y):
        if x is None or y is None:
            return None
        return x + y

    def mulMindNone(x, y):
        if x is None or y is None:
            return None
        return x * y

    angles = []
    angles.append(addMindNone(RElbowRoll, -1.8))
    angles.append(mulMindNone(-1, RShoulderRoll))
    angles.append(addMindNone(LElbowRoll, 1.8))
    angles.append(mulMindNone(-1, LShoulderRoll))
    angles.append(-0.7)
    angles.append(0.7)

    print(angles)
    return angles

def getAnglesFromPoints2(points):
    xs=[]
    ys=[]
    for i, (x, y) in enumerate(points):
        if i == 2 or i == 3 or i == 4 or i==5 or i==6 or i==7 or i==8 or i==11:
            xs.append(x)
            ys.append(y)
    print(points)
    print(xs)
    print(ys)

    #RElbowRoll and RShoulderRoll
    PRElbow=Vector(xs[1],ys[1],xs[0],ys[0])
    QRElbow=Vector(xs[1],ys[1],xs[2],ys[2])
    PRShoulder=Vector(xs[0],ys[0],xs[6],ys[6])
    QRShoulder=Vector(xs[0],ys[0],xs[1],ys[1])

    #LElbowRoll and lShoulderRoll
    PLElbow=Vector(xs[4],ys[4],xs[3],ys[3])
    QLElbow=Vector(xs[4],ys[4],xs[5],ys[5])
    PLShoulder=Vector(xs[3],ys[3],xs[7],ys[7])
    QLShoulder=Vector(xs[3],ys[3],xs[4],ys[4])

    #Variables
    RElbowRoll=angle(PRElbow.vector, QRElbow.vector)
    LElbowRoll=angle(PLElbow.vector, QLElbow.vector)
    RShoulderRoll = angle(PRShoulder.vector, QRShoulder.vector)
    LShoulderRoll = angle(PLShoulder.vector, QLShoulder.vector)

    angles = []
    angles.append(RElbowRoll-1.8)
    angles.append(-1*RShoulderRoll)
    angles.append(LElbowRoll+1.8)
    angles.append(-1*LShoulderRoll)
    angles.append(-0.7)
    angles.append(0.7)

    print(angles)
    return angles

cap = None
root = tk.Tk()
root.title('MrMime2')
root.geometry('960x540') #SD
root.config(bg='#C19BA6')
root.resizable(0,0)
def retarget():
    global points, lblVideo, frame
    processed, points = pose_estimation(frame)
    im = Image.fromarray(frame)
    img3 = ImageTk.PhotoImage(image=im)
    angles = getAnglesFromPoints(points)
    valid_idx = [i for i, v in enumerate(angles) if v is not None]
    valid_names = [names[x] for x in valid_idx]
    valid_angles = [angles[x] for x in valid_idx]
    Motion.setAngles(valid_names, valid_angles, 1.0)

def visualizar2():
    global cap, points, lblVideo, img, frame2, flag
    if flag == 2:
        lblVideo.image = ""
        cap.release()
        cv.destroyAllWindows()
        lblVideo.destroy()
        cap = cv.VideoCapture(0)
    flag = 3
    if cap is not None:
        ret, frame2 = cap.read()
        if ret == True:
            frame2 = imutils.resize(frame2, width=320)
            frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)
            im = Image.fromarray(frame2)
            img = ImageTk.PhotoImage(image=im)
            lblVideo = tk.Label(root)
            lblVideo.place(x=80, y=120)
            lblVideo.configure(image=img)
            lblVideo.image = img
            lblVideo.after(10, visualizar2)

def visualizar():
    global cap, points, lblVideo, img, frame1, flag
    if flag == 3:
        lblVideo.image = ""
        cap.release()
        cv.destroyAllWindows()
        lblVideo.destroy()
        cap = cv.VideoCapture(0)
    flag = 2
    if cap is not None:
        ret, frame1 = cap.read()
        if ret == True:
            frame1 = imutils.resize(frame1, width=320)
            frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
            lblVideo = tk.Label(root)
            lblVideo.place(x=80, y=120)
            frame1, points = pose_estimation(frame1)
            im = Image.fromarray(frame1)
            img = ImageTk.PhotoImage(image=im)
            lblVideo.configure(image=img)
            lblVideo.image = img
            lblVideo.after(10, visualizar)

def iniciar():
    global cap, img, btn_hpe2, btn_hpe1
    cap = cv.VideoCapture(0)
    if flag == 1:
        my_label.destroy()
        my_image_label.destroy()
        my_image_label2.destroy()
        btn_hpe.destroy()

    btn_hpe2 = tk.Button(root, text = "Activar HPE", command = visualizar, fg="black", bg="white", font="Helvetica 10 bold")
    btn_hpe2.config(height=3, width = 20)
    btn_hpe2.place(x=400, y=100)
    btn_hpe1 = tk.Button(root, text = "Desactivar HPE", command = visualizar2, fg="black", bg="white", font="Helvetica 10 bold")
    btn_hpe1.config(height=3, width = 20)
    btn_hpe1.place(x=700, y=100)

def hpe ():
    global my_image2, my_image_label2, points, img
    img2, points = pose_estimation(img)
    img = imutils.resize(img, width= 200,height= 200)
    image = imutils.resize(img, width= 200,height= 200)
    im = Image.fromarray(image)
    my_image2 = ImageTk.PhotoImage(image= im)
    my_image_label2 = tk.Label()
    my_image_label2.config(image= my_image2)
    my_image_label2.place(x=380, y=200)
    my_image_label2.image = img
    print(points)
    if points and flag==1:
        angles = getAnglesFromPoints2(points)
        Motion.wakeUp()
        #Motion.moveInit()
        #Motion.post.moveTo(0.5, 0, 0)
        Speech.say("Hola a todos!!")
        Motion.angleInterpolation(names, angles, times, True)
        #for i in range(3):
        #Motion.angleInterpolation(names, [-3.0, 1.2, -0.7], times, True)
        #Motion.angleInterpolation(names, [-1.0, 1.2, -0.7], times, True)
        Motion.rest()
    else:
        print ("no")

def open():
    global my_image, my_image_label, my_label, btn_hpe,img, flag, lblVideo, cap, btn_hpe1, btn_hpe2
    if flag == 2 or flag == 3:
        cap.release()
        cv.destroyAllWindows()
        lblVideo.destroy()
        btn_hpe2.destroy()
        btn_hpe1.destroy()
    flag = 1
    root.filename = filedialog.askopenfilename(title="Select a File", filetypes=[("jpg files", ".jpg"),("image", ".png")])
    my_label = tk.Label(root, text="Ruta de la imagen: \n\n" + root.filename, fg="black", bg="white", font='Helvetica 10 bold')
    my_label.place(x=0, y=25)
    img=cv.imread(root.filename)
    my_image = ImageTk.PhotoImage(Image.open(root.filename).resize((200, 200)))
    my_image_label = tk.Label(image=my_image)
    my_image_label.place(x=80, y=100)
    btn_hpe = tk.Button(root, text = "Activar HPE", command = hpe, fg="black", bg="white", font="Helvetica 10 bold")
    btn_hpe.config(height=3, width = 20)
    btn_hpe.place(x=400, y=100)

my_btn = tk.Button(root, text = "Cargar Archivo", command = open, fg="black", bg="white", font="Helvetica 10 bold")
my_btn.config(height=3,width=20)
my_btn.place(x= 400, y=20)
my_btn2 = tk.Button(root, text = "Usar Camara", command = iniciar, fg="black", bg="white", font="Helvetica 10 bold")
my_btn2.config(height=3, width=20)
my_btn2.place(x=720, y = 20)

###########################################################################

root.mainloop()

###########################################################################