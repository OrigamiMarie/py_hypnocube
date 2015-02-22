import time
from cube_connector import HypnocubeConnection
from command_code import CommandCode
from cube_animator import CubeAnimator
from cube_model import Color
from animations.random_animation import RandomAnimation
from animations.gradual_scramble import GradualScramble
from animations.cube_traversal import CubeTraversal
from animations.color_sorting import ColorSorting
from animations.season_lights import *


connection = HypnocubeConnection("/dev/cu.usbmodem1421", 40000)
connection.login()

#light_show = SeasonLights.get_default_lights()
#animator = CubeAnimator(connection, light_show)
#animator = CubeAnimator(connection, CubeTraversal(True))
animator = CubeAnimator(connection, ColorSorting(4))
#animator = CubeAnimator(connection, GradualScramble())
animator.run()


connection.close()

