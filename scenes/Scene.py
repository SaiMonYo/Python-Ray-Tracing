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
            if not line.startswith("//"):
                line = ast.literal_eval(line)
                objs.append(shape_lookup[line[0]](*line[1]))
        return objs

    def __iter__(self):
        yield from self.objects

    def __getitem__(self, n):
        return self.objects[n]
