import vector
import math
from PIL import Image


class Sphere:
    def __init__(self, center, radius, colour, reflectivity):
        self._colour = colour
        self.center = center
        self.radius = radius
        self.reflectivity = reflectivity

    def intersect(self, ray):
        '''returns the point of intersection and the time step for ray to hit sphere
           if it does not hit None, -1 is returned'''
        oc = vector.sub(ray.origin, self.center)
        a = vector.dot(ray.dir, ray.dir)
        b = 2 * vector.dot(oc, ray.dir)
        c = vector.dot(oc, oc) - self.radius * self.radius
        disc = b * b - 4 * a * c
        if disc >= 0 and a != 0:
            t = (-b - math.sqrt(disc)) / (2.0*a)
            return vector.add(ray.origin, vector.multn(ray.dir, t)), t
        return None, -1

    def normal(self, p):
        '''return normal of sphere at a point p'''
        return vector.normalise(vector.sub(p, self.center))

    def colour(self, *args):
        '''return colour of the object'''
        return self._colour


class Skysphere:
    def __init__(self, center, radius, file_name):
        self.center = center
        self.radius = radius
        img = Image.open(file_name).convert("RGB")
        self.image_width = img.width
        self.image_height = img.height
        temp = list(img.getdata())
        self.image_array = []
        for i in range(0, len(temp) // self.image_width):
            self.image_array.append(temp[i * self.image_width:(i+1) * self.image_width])

    def intersect(self, ray):
        '''returns the point of intersection and the time step for ray to hit sphere
           if it does not hit None, -1 is returned'''
        oc = vector.sub(ray.origin, self.center)
        a = vector.dot(ray.dir, ray.dir)
        b = 2 * vector.dot(oc, ray.dir)
        c = vector.dot(oc, oc) - self.radius * self.radius
        disc = b * b - 4 * a * c
        if disc >= 0 and a != 0:
            # calculate both time steps as we are inside sphere
            t0 = (-b - math.sqrt(disc)) / (2.0*a)
            t1 = (-b + math.sqrt(disc)) / (2.0*a)
            t = vector.min_positive(t0, t1)
            return vector.add(ray.origin, vector.multn(ray.dir, t)), t
        return None, -1

    def normal(self, p):
        '''return normal of sphere at a point p'''
        return vector.normalise(vector.sub(p, self.center))

    def colour(self, intersection):
        '''return pixel colour at intersection point'''
        # Done by using UV mapping
        d = vector.normalise(vector.sub(intersection, self.center))
        u = 0.5 + (math.atan2(d[0], d[2])) / (2 * math.pi)
        v = 0.5 - (math.asin(d[1])) / math.pi
        u *= self.image_width - 1
        v *= self.image_height - 1
        u, v = int(u), int(v)
        return self.image_array[v][u]


class Skybox:
    def __init__(self):
        pass
    

class Plane:
    def __init__(self, coords, colours, reflectivity):
        self.coords = coords
        self.colours = colours
        self.reflectivity = reflectivity
        self._normal = (0, 1, 0)

    def intersect(self, ray):
        '''return the intersection and time step of that point of a ray and the plane
           None, -1 is returned if it isnt hit'''
        denom = vector.dot(ray.dir, self._normal)
        if abs(denom) < 0.000001:
            return None, -1
        t = vector.dot(vector.sub(self.coords, ray.origin), self._normal) / denom
        if t < 0:
            return None, -1
        return vector.add(ray.origin, vector.multn(ray.dir, t)), t

    def colour(self, p):
        '''return colour at point p, if 2 colours where provided then checkerboard is applied'''
        if len(self.colours) == 2:
            return self.colours[0] if (int(p[0] * 2) % 2) == (int(p[2] * 2) % 2) else self.colours[1]
        else:
            return self.colours[0]

    def normal(self, intersection):
        '''returns normal at the point of intersection'''
        return (0, 1, 0)