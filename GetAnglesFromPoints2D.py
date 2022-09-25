import math
import numpy as np

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

# RShoulder, RElbow, RWrist, LShoulder, LElbow, LWrist, RHip, LHip
mppose_idxes = [12, 14, 16, 11, 13, 15, 24, 23]
names = ['RElbowRoll', 'RShoulderRoll', 'LElbowRoll', 'LShoulderRoll','RElbowYaw','LElbowYaw']

def get_angles_from_results_2d(landmark_tuples):
    xs=[]
    ys=[]

    if not landmark_tuples or len(landmark_tuples) != 33:
        return [None] * len(names)

    for idx in mppose_idxes: 
        landmark = landmark_tuples[idx]
        xs.append(landmark[0])
        ys.append(landmark[1])

    # print(xs)
    # print(ys)

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
    angles.append(mulMindNone(addMindNone(RElbowRoll, -1.8), -1))
    angles.append(mulMindNone(-1, RShoulderRoll))
    angles.append(addMindNone(LElbowRoll, 1.8))
    angles.append(mulMindNone(-1, LShoulderRoll))
    angles.append(-0.7)
    angles.append(0.7)

    print('angles:', angles)
    return angles