import pprint

class CubeModel:

    def __init__(self, edge_length=4, duration=0.1):
        """
        CubeModel initializer

        edge_length defaults to 4, because right now you can only buy the 4x4x4 version.  

        duration is how long this set of colors should show up on the cube.  
        """
        self.duration = duration
        black = Color(0, 0, 0)
        self.n = n
        # Initialize the nXnXn cube.  
        self.cube = [[[black for k in xrange(self.n)] 
                      for j in xrange(self.n)] 
                      for i in xrange(self.n)]
        

    def set_pixel(self, x, y, z, color):
        """
        Pretty simple.  Set the given x, y, z coordinates to the given Color.  
        Bad things happen if you pass in coordinates that are out of bounds 
        or a thing that is not a color.  
        """
        self.cube[x][y][z] = color


    def get_pixel(self, x, y, z):
        """
        Get the Color of the pixel at x, y, z coordinates.  
        Bad things happen if you pass in coordinates that are out of bounds.  
        """
        return self.cube[x][y][z]

    def get_pretty_print(self):
        """
        Uses pformat to make a tolerable-looking printout of this cube's colors.  
        """
        return pprint.pformat(self.cube)

class Color:

    def __init__(self, r, g, b):
        """
        Initializer for Color.  
        Simple r (red), g (green), and b (blue).
        If you send numbers that are out of range (0 to 15 inclusive), 
        this will throw a ColorError.  
        """
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

    def __repr__(self):
        return str(self.color)


