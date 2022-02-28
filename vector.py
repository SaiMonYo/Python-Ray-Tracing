import math

class Ray:
    def __init__(self, origin, dir):
        self.origin = origin
        self.dir = dir

    def __hash__(self):
        return hash(self.origin) + hash(self.dir)

    def __str__(self):
        return f"origin: {self.origin}, direction: {self.dir}"


def sub(va, vb):
    '''return va - vb'''
    return (va[0] - vb[0], va[1] - vb[1], va[2] - vb[2])

def add(va, vb):
    '''return va + vb'''
    return (va[0] + vb[0], va[1] + vb[1], va[2] + vb[2])

def multn(v, n):
    '''return v * n'''
    return (v[0] * n, v[1] * n, v[2] * n)

def divn(v, n):
    '''return v / n'''
    return (v[0] / n, v[1] / n, v[2] / n)

def dot(va, vb):
    '''return the dot product of va.vb'''
    return va[0]*vb[0] + va[1]*vb[1] + va[2]*vb[2]

def length(v):
    '''return length of vector v'''
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def normalise(v):
    '''return normalised vector v'''
    return divn(v, length(v))

def angle_between(va, vb):
    '''calculates angle between two vectors va, vb'''
    return dot(va, vb) / (length(va) * length(vb))

def boundn(n, low, high):
    '''bounds a number between low and high'''
    return max(low, min(high, n))

def bound(va, low, high):
    '''bounds a vectors components between low and high'''
    return (boundn(va[0], low, high), boundn(va[1], low, high), boundn(va[2], low, high))

def min_positive(va, vb):
    '''return the minimum number over 0, returns va if neither over 0'''
    if va < 0:
        return vb
    return va

def rotate_around_X(v, angle):
    '''rotate vector around X axis by angle'''
    c = math.cos(angle)
    s = math.sin(angle)
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)

def rotate_around_Y(v, angle):
    '''rotate vector around Y axis by angle'''
    c = math.cos(angle)
    s = math.sin(angle)
    return (v[0] * c + v[2] * s,  v[1], -s * v[0] + v[2] * c)

def rotate_around_Z(v, angle):
    '''rotate vector around Z axis by angle'''
    c = math.cos(angle)
    s = math.sin(angle)
    return (v[0] * c + v[2] * s,  v[1], -s * v[0] + v[2] * c)