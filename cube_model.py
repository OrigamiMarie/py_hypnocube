
class CubeModel:

    def __init__(self):
        black = Color(0, 0, 0)
        self.n = 4
        # Initialize the 4x4x4 cube.  
        self.cube = [[[black for k in xrange(self.n)] 
                      for j in xrange(self.n)] 
                      for i in xrange(self.n)]
        
    def set_pixel(self, x, y, z, color):
        self.cube[x][y][z] = color


class Color:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        if(r > 15 or g > 15 or b > 15 or r < 0 or g < 0 or b < 0):
            raise ColorError(self)

    def __str__(self):
        return "R:%x/G:%x/B:%x|" % (self.r, self.g, self.b)

    def __repr__(self):
        return "R:%x/G:%x/B:%x|" % (self.r, self.g, self.b)

class ColorError(Exception):

    def __init__(self, color):
        self.color = color

    def __str__(self):
        return str(self.color)


