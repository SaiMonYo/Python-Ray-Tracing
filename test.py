import vector, pygame, os, time
from settings import *
from functools import cache
from scenes.Scene import *
from shapes import *
from PIL import Image
import numpy as np


@cache
def trace(cam, SCALE):
    PROJ_WIDTH = (WIDTH) // SCALE
    PROJ_HEIGHT = (HEIGHT) // SCALE
    CAM_DIST = -(PROJ_HEIGHT // 2) / TAN_A
    screen = []
    z = 0
    for x in range(PROJ_WIDTH+1):
        for y in range(PROJ_HEIGHT+1):
            ray0 = vector.Ray(cam, vector.normalise((x - PROJ_WIDTH // 2, PROJ_HEIGHT // 2 - y, CAM_DIST)))
            col = (0, 0, 0)
            reflection = 1
            for i in range(100):
                z = max(i, z)
                t = float("inf")
                # intersections
                for i, obj in enumerate(objects):
                    obj_intersection, obj_t = obj.intersect(ray0)
                    # first ray intersection
                    if 0 < obj_t < t:
                        t = obj_t
                        intersection = obj_intersection
                        ind = i
                if type(objects[ind]) == Skysphere or type(objects[ind]) == Skybox:
                    colour = objects[ind].colour(intersection)
                    col = vector.add(col, vector.multn(colour, reflection))
                    break
                # doesnt intersect
                if t == float("inf"):
                    break
                # cast ray from intersection to light to see if in shadow
                ray1 = vector.Ray(intersection, vector.normalise(vector.sub(light, intersection)))
                t1 = float("inf")
                for i, obj in enumerate(objects):
                    # avoid self shadowing
                    if i == ind:
                        continue
                    obj_intersection_shadow, obj_t_shadow = obj.intersect(ray1)
                    if 0 < obj_t_shadow < t:
                        t1 = obj_t_shadow
                        intersection = obj_intersection_shadow
                # in shadow
                if t1 < float("inf"):
                    colour = vector.multn(objects[ind].colour(intersection), 0.06)
                    col = vector.add(col, vector.multn(colour, reflection))
                    break
                # diffuse shading
                L = vector.normalise(vector.sub(light, intersection))
                N = objects[ind].normal(intersection)
                colour = vector.divn(objects[ind].colour(intersection), 255)
                dotNL = max(vector.dot(N, L), 0)
                colour = vector.bound(vector.multn(colour, max(dotNL + 0.1, 0)/1.1), 0, 1)
                colour = vector.multn(colour, 255)

                # reflection
                ray0 = vector.Ray(vector.add(intersection, vector.multn(N, 0.0001)), vector.normalise(vector.sub(ray0.dir, vector.multn(N, 2 * vector.dot(ray0.dir, N)))))
                col = vector.add(col, vector.multn(colour, reflection))
                reflection *= objects[ind].reflectivity
            screen.append((vector.bound(col, 0, 255), x * SCALE, y * SCALE))
    print(z)
    return screen

def draw(win, cam, save = False):
    win.fill((0, 0, 0))
    pixels = trace(cam, SCALE)
    for c, x, y in pixels:
        #pygame.draw.circle(win, c, (x,y), 1)
        pygame.draw.rect(win, c, (x,y,SCALE,SCALE))
    pygame.display.flip()
    if save:
        img = Image.new("RGB", ((WIDTH), (HEIGHT)))
        new_pixels = img.load()
        for c, x, y in pixels:
            try:
                new_pixels[x, y] = (int(c[0]), int(c[1]), int(c[2]), 255)
            except:
                pass
        img.save("wow.png")


objects = Scene("scenes/spheres.scene")

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()

win = pygame.display.set_mode((WIDTH, HEIGHT))
cam = (0, -0.5, -1.5)
light = (-3.0, 15.0, 2.5)


SCALE = 16
changed = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if changed:
        t = time.time()
        if SCALE == 1:
            draw(win, cam, True)
        else:
            draw(win, cam, False)
        pygame.display.flip()
        print(time.time() - t)
        changed = False
    keys = pygame.key.get_pressed()
    if any(keys):
        changed = True
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_UP]:
            SCALE -= 1
            if SCALE < 1:
                SCALE = 1
        if keys[pygame.K_DOWN]:
            SCALE += 1
            if WIDTH // SCALE < 4:
                SCALE -= 1
        if keys[pygame.K_w]:
            cam = (cam[0], cam[1], cam[2]-0.1)
        if keys[pygame.K_s]:
            cam = (cam[0], cam[1], cam[2]+0.1)
        if keys[pygame.K_a]:
            cam = (cam[0]-0.1, cam[1], cam[2])
        if keys[pygame.K_d]:
            cam = (cam[0]+0.1, cam[1], cam[2])
    pygame.event.pump()