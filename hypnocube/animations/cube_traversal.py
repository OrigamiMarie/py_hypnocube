import copy
from hypnocube.cube_model import *

class CubeTraversal:

    def __init__(self, blink, edge_length=4):
        self.blink = blink
        self.n = edge_length

        black = CubeModel(self.n, 1)
        red = CubeModel(self.n, 1)
        green = CubeModel(self.n, 1)
        blue = CubeModel(self.n, 1)
        cyan = CubeModel(self.n, 1)
        yellow = CubeModel(self.n, 1)
        magenta = CubeModel(self.n, 1)
        white = CubeModel(self.n, 1)
        
        # Just to shorten the variable name
        n = self.n-1
        for i in xrange(0, edge_length):
            for j in xrange(0, edge_length):
                for k in xrange(0, edge_length):
                    black.set_pixel(i, j, k, Color(i, j, k))
                    blue.set_pixel(i, j, n-k, Color(i, j, 15-k))
                    green.set_pixel(i, n-j, k, Color(i, 15-j, k))
                    cyan.set_pixel(i, n-j, n-k, Color(i, 15-j, 15-k))
                    red.set_pixel(n-i, j, k, Color(15-i, j, k))
                    magenta.set_pixel(n-i, j, n-k, Color(15-i, j, 15-k))
                    yellow.set_pixel(n-i, n-j, k, Color(15-i, 15-j, k))
                    white.set_pixel(n-i, n-j, n-k, Color(15-i, 15-j, 15-k))
        self.sequence = [white, magenta, yellow, white, cyan, magenta, 
                         red, yellow, cyan, white, red, green, 
                         yellow, black, green, blue, magenta, black, 
                        red, blue, black, blue, cyan, green]

        black_hot_corner = [0, 0, 0]
        blue_hot_corner = [0, 0, n]
        green_hot_corner = [0, n, 0]
        cyan_hot_corner = [0, n, n]
        red_hot_corner = [n, 0, 0]
        magenta_hot_corner = [n, 0, n]
        yellow_hot_corner = [n, n, 0]
        white_hot_corner = [n, n, n]

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
        cube = CubeModel(self.n, 1)
        cube.cube = copy.deepcopy(self.sequence[0].cube)
        increment_cube = [[[[] for k in xrange(0, self.n)]
                      for j in xrange(0, self.n)]
                      for i in xrange(0, self.n)]
        c = 0
        while 1==1:
            c = (c + 1) % 24
            for i in xrange(0, self.n):
                for j in xrange(0, self.n):
                    for k in xrange(0, self.n):
                        start_color = cube.get_pixel(i, j, k)
                        end_color = self.sequence[c].get_pixel(i, j, k)
                        color_diffs = [(end_color.r - start_color.r)/12,
                                       (end_color.g - start_color.g)/12,
                                       (end_color.b - start_color.b)/12]
                        increment_cube[i][j][k] = color_diffs

            for s in xrange(0, 16-self.n):
                for i in xrange(0, self.n):
                    for j in xrange(0, self.n):
                        for k in xrange(0, self.n):
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

            



