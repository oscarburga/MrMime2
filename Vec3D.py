import numpy as np
import math


class Vec3:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.coords = np.asarray([x, y, z], dtype=float)

    def __repr__(self):
        return f'{self.coords}'

    def __getattr__(self, key):
        try:
            idx = ['x', 'y', 'z'].index(key)
        except ValueError as ve:
            raise AttributeError
            return None
        return self.coords[idx]

    def __add__(self, other):
        return Vec3(*(self.coords + other.coords))

    def __sub__(self, other):
        return Vec3(*(self.coords - other.coords))

    def __mul__(self, other):
        if isinstance(other, Vec3):
            return np.dot(self.coords, other.coords)
        return Vec3(*(self.coords * other))

    def __truediv__(self, other):
        return Vec3(*(self.coords / other))

    def __mod__(self, other):
        return self.cross(other)

    def __neg__(self):
        return self * -1.0

    def dot(self, other):
        return self * other

    def cross(self, other):
        return Vec3(*np.cross(self.coords, other.coords))

    def size(self):
        return np.linalg.norm(self.coords)

    def size2(self):
        return self * self

    def project_onto_vector(self, other):
        assert isinstance(other, Vec3)
        k = (self * other) / (other * other)
        return other * k

    def project_onto_plane(self, normal):
        assert isinstance(normal, Vec3)
        return self - self.project_onto_vector(normal)

    def rotate_around_vector(self, other, angle):
        assert isinstance(other, Vec3)
        a_parallel_b = self.project_onto_vector(other)
        a_ortho_b = self - a_parallel_b
        w = other % a_ortho_b
        a_ortho_b_size = a_ortho_b.size()
        x1 = np.cos(angle) / a_ortho_b_size
        x2 = np.sin(angle) / w.size()
        rot_a_ortho_b = ((a_ortho_b * x1) + (w * x2)) * a_ortho_b_size
        return a_parallel_b + rot_a_ortho_b

    def get_normal(self):
        return Vec3(*(self.coords / self.size()))

    @staticmethod
    def angle(u, v) -> float:
        """ Returns the unsigned angle between @u and @v """
        dot = u * v
        len_prod = u.size() * v.size()
        return math.acos(dot / len_prod)

    @staticmethod
    def signed_angle(u, v, up) -> float:
        """ Signed angle from vector @u to vector @v on the plane defined by the up vector"""
        return math.atan2(u.cross(v) * up, u * v)


if __name__ == '__main__':
    around = -Vec3(0.0, 1.0, 0.0)
    to_rot = Vec3(1.0, 0.0, 0.0)

    import math
    print(to_rot.rotate_around_vector(around, math.pi))
    print(to_rot.rotate_around_vector(around, math.pi / 2.0))
    print(to_rot.rotate_around_vector(around, -math.pi / 2.0))
    print(to_rot.rotate_around_vector(around, -math.pi))
