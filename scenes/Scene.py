import sys, os, ast
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shapes

shape_lookup = {"Sphere": shapes.Sphere, "Plane": shapes.Plane, "Skysphere": shapes.Skysphere}

class Scene:
    def __init__(self, scene_file):
        self.objects = self.parse_scene(scene_file)

    def parse_scene(self, scene_file):
        '''parse a scene from a file'''
        objs = []
        with open(scene_file) as file:
            raw_data = file.read().split("\n")
        for line in raw_data:
            # commented out lines start with //
            if not line.startswith("//") and "Cam" not in line and "Light" not in line:
                line = ast.literal_eval(line)
                objs.append(shape_lookup[line[0]](*line[1]))
            if "Cam" in line:
                line = ast.literal_eval(line)
                self.cam = line[1]
            elif "Light" in line:
                line = ast.literal_eval(line)
                self.light = line[1]
        return objs

    def __iter__(self):
        yield from self.objects

    def __getitem__(self, n):
        return self.objects[n]
