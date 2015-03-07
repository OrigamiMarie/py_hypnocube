import random
from hypnocube.cube_model import *


class RandomAnimation:
    
    def next_cube(self):
        while 1==1:
            yield self.make_random_cube()


    def make_random_cube(self):
        cube = CubeModel(4, 1)
        r = [0, 5, 10, 15]
        g = [0, 4, 8, 12]
        b = [0, 2, 7, 15]
        for x in xrange(0, 4):
            for y in xrange(0, 4):
                for z in xrange(0, 4):
                    cube.set_pixel(x, y, z, Color((2**random.randint(0, 4))-1,
                                                  (2**random.randint(0, 4))-1,
                                                  (2**random.randint(0, 4))-1))
        return cube

