import copy
from cube_model import *

class CubeTraversal:

    def __init__(self, blink):
        self.blink = blink

        black = CubeModel(4, 1)
        red = CubeModel(4, 1)
        green = CubeModel(4, 1)
        blue = CubeModel(4, 1)
        cyan = CubeModel(4, 1)
        yellow = CubeModel(4, 1)
        magenta = CubeModel(4, 1)
        white = CubeModel(4, 1)
        
                                  
        for i in xrange(0, 4):
            for j in xrange(0, 4):
                for k in xrange(0, 4):
                    black.set_pixel(i, j, k, Color(i, j, k))
                    blue.set_pixel(i, j, 3-k, Color(i, j, 15-k))
                    green.set_pixel(i, 3-j, k, Color(i, 15-j, k))
                    cyan.set_pixel(i, 3-j, 3-k, Color(i, 15-j, 15-k))
                    red.set_pixel(3-i, j, k, Color(15-i, j, k))
                    magenta.set_pixel(3-i, j, 3-k, Color(15-i, j, 15-k))
                    yellow.set_pixel(3-i, 3-j, k, Color(15-i, 15-j, k))
                    white.set_pixel(3-i, 3-j, 3-k, Color(15-i, 15-j, 15-k))
        self.sequence = [white, magenta, yellow, white, cyan, magenta, 
                         red, yellow, cyan, white, red, green, 
                         yellow, black, green, blue, magenta, black, 
                        red, blue, black, blue, cyan, green]

        black_hot_corner = [0, 0, 0]
        blue_hot_corner = [0, 0, 3]
        green_hot_corner = [0, 3, 0]
        cyan_hot_corner = [0, 3, 3]
        red_hot_corner = [3, 0, 0]
        magenta_hot_corner = [3, 0, 3]
        yellow_hot_corner = [3, 3, 0]
        white_hot_corner = [3, 3, 3]

        # There are certainly better ways of doing this.  
        self.hot_corners_sequence = [white_hot_corner, magenta_hot_corner, 
                                     yellow_hot_corner, white_hot_corner,
                                     cyan_hot_corner, magenta_hot_corner,
                                     red_hot_corner, yellow_hot_corner,
                                     cyan_hot_corner, white_hot_corner,
                                     red_hot_corner, green_hot_corner,
                                     yellow_hot_corner, black_hot_corner,
                                     green_hot_corner, blue_hot_corner,
                                     magenta_hot_corner, black_hot_corner,
                                     red_hot_corner, blue_hot_corner,
                                     black_hot_corner, blue_hot_corner,
                                     cyan_hot_corner, green_hot_corner]

    def next_cube(self):
        cube = CubeModel(4, 1)
        cube.cube = copy.deepcopy(self.sequence[0].cube)
        increment_cube = [[[[] for k in xrange(0, 4)]
                      for j in xrange(0, 4)]
                      for i in xrange(0, 4)]
        c = 0
        ######  Uh-oh, you need to learn about array copying!  
        ######  You need copies of cubes so that you don't mess up the original.
        ######  Probably.  There are other crazier options.  
        while 1==1:
            c = (c + 1) % 24
            for i in xrange(0, 4):
                for j in xrange(0, 4):
                    for k in xrange(0, 4):
                        start_color = cube.get_pixel(i, j, k)
                        end_color = self.sequence[c].get_pixel(i, j, k)
                        color_diffs = [(end_color.r - start_color.r)/12,
                                       (end_color.g - start_color.g)/12,
                                       (end_color.b - start_color.b)/12]
                        increment_cube[i][j][k] = color_diffs

            for s in xrange(0, 12):
                for i in xrange(0, 4):
                    for j in xrange(0, 4):
                        for k in xrange(0, 4):
                            # Modifying color in place, don't need to set it.
                            color = cube.get_pixel(i, j, k)
                            color.r = color.r + increment_cube[i][j][k][0]
                            color.g = color.g + increment_cube[i][j][k][1]
                            color.b = color.b + increment_cube[i][j][k][2]
                yield cube

            if self.blink:
                yield cube
                hot_corner = self.hot_corners_sequence[c]
                temp_color = cube.get_pixel(hot_corner[0], hot_corner[1], 
                                            hot_corner[2])
                cube.set_pixel(hot_corner[0], hot_corner[1], hot_corner[2],
                               Color(0, 0, 0))
                yield cube
                cube.set_pixel(hot_corner[0], hot_corner[1], hot_corner[2],
                              temp_color)
                yield cube
                yield cube

            



