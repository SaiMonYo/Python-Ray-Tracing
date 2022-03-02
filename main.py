import vector, pygame, os
from settings import *
from functools import cache
from scenes.Scene import *
from shapes import *
from PIL import Image


reflection_depth = 100
@cache
def trace(cam, SCALE, phi, width, height):
    PROJ_WIDTH = (width) // SCALE
    PROJ_HEIGHT = (height) // SCALE
    CAM_DIST = (-(PROJ_HEIGHT // 2) / TAN_A)
    screen = []
    for x in range(PROJ_WIDTH + 1):
        for y in range(PROJ_HEIGHT + 1):
            # set the ray to go through x, y pixel on screen
            direction = vector.normalise((x - PROJ_WIDTH // 2, PROJ_HEIGHT // 2 - y, CAM_DIST))
            # rotate by phi
            direction = vector.rotate_around_Y(direction, phi)
            ray0 = vector.Ray(cam, direction)
            pixel_colour = (0, 0, 0)
            reflectiveness = 1
            for i in range(reflection_depth):
                t = float("inf")
                # intersections
                for i, obj in enumerate(objects):
                    obj_intersection, obj_t = obj.intersect(ray0)
                    # first ray intersection
                    if 0 < obj_t < t:
                        t = obj_t
                        intersection = obj_intersection
                        ind = i
                # doesnt intersect
                if t == float("inf"):
                    break
                # no shading or reflection from a skybox/skysphere
                if type(objects[ind]) == Skysphere or type(objects[ind]) == Skybox:
                    ray_colour = objects[ind].colour(intersection)
                    pixel_colour = vector.add(pixel_colour, vector.multn(ray_colour, reflectiveness))
                    break

                # cast ray from intersection to light to see if in shadow
                light_to_point = vector.normalise(vector.sub(objects.light, intersection))
                shadow_ray = vector.Ray(intersection, light_to_point)
                t1 = float("inf")
                for i, obj in enumerate(objects):
                    # avoid self shadowing
                    if i == ind:
                        continue
                    obj_intersection_shadow, obj_t_shadow = obj.intersect(shadow_ray)
                    if 0 < obj_t_shadow < t:
                        t1 = obj_t_shadow
                        intersection_shadow = obj_intersection_shadow
                # in shadow
                if t1 < float("inf"):
                    ray_colour = vector.multn(objects[ind].colour(intersection_shadow), 0.06)
                    pixel_colour = vector.add(pixel_colour, vector.multn(ray_colour, reflectiveness))
                    break

                # diffuse shading (shading based on normal from point to light)
                normal_vector = objects[ind].normal(intersection)
                ray_colour = vector.divn(objects[ind].colour(intersection), 255)
                dotted = max(vector.dot(normal_vector, light_to_point), 0)
                ray_colour = vector.bound(vector.multn(ray_colour, max(dotted + 0.1, 0)/1.1), 0, 1)
                ray_colour = vector.multn(ray_colour, 255)

                # specular lighting (lighting based on the angle between light reflection and camera)
                camera_vector = vector.normalise(vector.sub(cam, intersection))
                light_vector = vector.normalise(vector.sub(intersection, objects.light))
                light_reflectivity_vector = vector.sub(light_vector, vector.multn(normal_vector, 2 * vector.dot(light_vector, normal_vector)))
                sf = vector.boundn(vector.dot(light_reflectivity_vector, camera_vector), 0, 1)
                pixel_colour = vector.add(pixel_colour, vector.multn((255,255,255), pow(sf, 3) * objects[ind].reflectivity * 0.4))
                
                # reflection
                direction = vector.normalise(vector.sub(ray0.dir, vector.multn(normal_vector, 2 * vector.dot(ray0.dir, normal_vector))))
                ray0 = vector.Ray(vector.add(intersection, vector.multn(normal_vector, 0.0001)), direction)
                pixel_colour = vector.add(pixel_colour, vector.multn(ray_colour, reflectiveness))
                reflectiveness *= objects[ind].reflectivity
            screen.append((vector.bound(pixel_colour, 0, 255), x * SCALE, y * SCALE))
    return screen

def save_image(pixels, file_name: str):
    '''save pixels to image file'''
    img = Image.new("RGB", ((WIDTH), (HEIGHT)))
    new_pixels = img.load()
    for c, x, y in pixels:
        new_pixels[x, y] = (int(c[0]), int(c[1]), int(c[2]), 255)
    if "." not in file_name:
        file_name += ".png"
    img.save(file_name)

@cache
def ssaa(cam, SCALE, phi, width, height, upscale = 1):
    '''supersampling anti aliasing, boost quality with a linear factor to time'''
    # a - the length multiplier
    a = upscale * 2 + 1
    factor = 1 / (a * a)
    pixels = trace(cam, SCALE, phi, width * a, height * a)
    pixel_lookup = {}
    for c, x, y in pixels:
        pixel_lookup[(x, y)] = c
    image = [[(0,0,0) for i in range(width)] for j in range(height)]
    for j in range(1, height):
        for i in range(1, width):
            for dj in range(-upscale, upscale + 1, 1):
                for di in range(-upscale, upscale + 1, 1):
                    x = i * a + di
                    y = j * a + dj
                    image[j][i] = vector.add(image[j][i], vector.multn(pixel_lookup[(x * SCALE , y * SCALE )], factor))
    pixels = []
    for j in range(1, height):
        for i in range(1, width):
            pixels.append((image[j][i], i, j))
    return pixels

def render_all(cam):
    '''Renders all the resolutions for current position and rotation'''
    for sc in range(1, WIDTH // 4):
        trace(cam, sc, phi, WIDTH, HEIGHT)

def draw(win, pixels, save = False):
    '''draw pixels to screen with optional save to image'''
    for c, x, y in pixels:
        #pygame.draw.circle(win, c, (x,y), 1)
        pygame.draw.rect(win, c, (x,y,SCALE,SCALE))
    pygame.display.flip()
    if save:
        save_image(pixels, "wow.png")

def cam_movement(cam, phi, d):
    '''move in relation to angle facing'''
    h = 0.1
    c = math.cos(phi) * h
    s = math.sin(phi) * h
    if d == "f":
        return vector.add(cam, (-s, 0, -c))
    if d == "b":
        return vector.add(cam, (s, 0, c))
    if d == "l":
        return vector.add(cam, (-c, 0, s))
    if d == "r":
        return vector.add(cam, (c, 0, -s))


if __name__ == "__main__":
    # load scene
    objects = Scene("scenes/spheres.scene")

    # set window position and initialise pygame objects
    os.environ['SDL_VIDEO_WINDOW_POS'] = "50,50"
    pygame.init()
    clock = pygame.time.Clock()
    win = pygame.display.set_mode((WIDTH, HEIGHT))


    SCALE = 1
    # phi: angle on x,z plane
    phi = 0
    dphi = math.pi / 30
    changed = True
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if changed:
            pixels = trace(objects.cam, SCALE, phi, WIDTH, HEIGHT)
            draw(win, pixels)
            pygame.display.flip()
            changed = False
        # handle key presses
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
                SCALE = max(SCALE, 15)
                objects.cam = cam_movement(objects.cam, phi, "f")
            if keys[pygame.K_s]:
                SCALE = max(SCALE, 15)
                objects.cam = cam_movement(objects.cam, phi, "b")
            if keys[pygame.K_a]:
                SCALE = max(SCALE, 15)
                objects.cam = cam_movement(objects.cam, phi, "l")
            if keys[pygame.K_d]:
                SCALE = max(SCALE, 15)
                objects.cam = cam_movement(objects.cam, phi, "r")
            if keys[pygame.K_LEFT]:
                SCALE = max(SCALE, 15)
                phi += dphi
                phi %= math.pi * 2
            if keys[pygame.K_RIGHT]:
                SCALE = max(SCALE, 15)
                phi -= dphi
                phi %= math.pi * 2
        pygame.event.pump()
