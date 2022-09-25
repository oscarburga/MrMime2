import numpy as np
import math
class Vector:
    X1 = 0
    Y1 = 0
    X2 = 0
    Y2 = 0
    vector = np.array([0,0])
    def __init__(self, X1, Y1, X2, Y2):
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

p = Vector(0,0,5,2)
q = Vector(0,0,3,6)

print(angle(p.vector,q.vector))