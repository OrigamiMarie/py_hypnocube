import random
from cube_model import *

class GradualScramble:

    def __init__(self):
        self.cube = CubeModel(4, 0.1)
        r = [0, 5, 10, 15]
        g = [0, 4, 8, 12]
        b = [0, 2, 7, 15]
        for x in xrange(0, 4):
            for y in xrange(0, 4):
                for z in xrange(0, 4):
                    self.cube.set_pixel(x, y, z, Color(r[x], g[y], b[z]))


    def next_cube(self):
        while 1==1:
            a = [random.randint(0, 3),      
                 random.randint(0, 3),
                 random.randint(0, 3)]
            b = [random.randint(0, 3), 
                 random.randint(0, 3), 
                 random.randint(0, 3)]
            temp = self.cube.get_pixel(a[0], a[1], a[2])
            self.cube.set_pixel(a[0], a[1], a[2], 
                                self.cube.get_pixel(b[0], b[1], b[2]))
            self.cube.set_pixel(b[0], b[1], b[2], temp)
            a = b
            yield self.cube
    
