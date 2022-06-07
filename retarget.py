from naoqi import ALProxy
# import matplotlib.pyplot as plt
import numpy as np
import math
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


inWidth=368
inHeight=368
thr=0.2
points=[]

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                ["Neck", "RHip"], ["Neck", "LHip"] ]

img=cv.imread("image.jpg")

# plt.imshow(img) 

# plt.imshow(cv.cvtColor(img,cv.COLOR_BGR2RGB))

def pose_estimation(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out=out[:, :19, :, :]
    
    assert(len(BODY_PARTS) <= out.shape[1])
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


cap=cv.VideoCapture(0)
# cap.set(cv.CAP_PROP_FPS,10)
# cap.set(3,800)
# cap.set(4,800)
# if not cap.isOpened():
#     cap=cv.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

###########################################################################
# NAO_HOST = "192.168.1.15"
NAO_HOST = "127.0.0.1"
NAO_PORT = 9559

names = ['RElbowRoll', 'RShoulderRoll', 'LElbowRoll', 'LShoulderRoll','RElbowYaw','LElbowYaw']
times = [[1.0], [1.2],[1.0], [1.2],[1.0], [1.2]]

Motion = ALProxy("ALMotion", NAO_HOST, NAO_PORT)
Motion.wakeUp()

while True:
    hasFrame,frame=cap.read()
    if not hasFrame:
        cv.waitKey()
        break
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    processed, points = pose_estimation(frame)
    cv.imshow("processed", processed)
    print(points)
    angles = getAnglesFromPoints(points)
    valid_idx = [i for i, v in enumerate(angles) if v is not None]
    valid_names = [names[x] for x in valid_idx]
    valid_angles = [angles[x] for x in valid_idx]
    Motion.setAngles(valid_names, valid_angles, 1.0)
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
    # Motion.setAngles(names, angles, times, True)