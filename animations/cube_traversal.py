
class CubeTraversal:

    def __init__(self):
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

    def run(self):
        i = 0
        ######  Uh-oh, you need to learn about array copying!  
        ######  You need copies of cubes so that you don't mess up the original.
        ######  Probably.  There are other crazier options.  
        while 1==1:
            i = (i + 1) % 24
