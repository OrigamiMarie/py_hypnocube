import time
from cube_connector import HypnocubeConnection
from cube_animator import CubeAnimator
from cube_model import Color
<<<<<<< HEAD
#from animations.random_animation import RandomAnimation
=======
from animations.random_animation import RandomAnimation
>>>>>>> d6d8c1bb20eae65fde2070867e3020f4e107420d
from animations.cube_traversal import CubeTraversal
from animations.color_sorting import ColorSorting
from animations.season_lights import *


connection = HypnocubeConnection("/dev/cu.usbmodem1411")

light_show = SeasonLights.get_default_lights()
#animator = CubeAnimator(connection, light_show)
#animator = CubeAnimator(connection, CubeTraversal(True))
animator = CubeAnimator(connection, ColorSorting(4))
animator.run()


connection.close()

