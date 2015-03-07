import argparse

from cube_animator import CubeAnimator
from cube_connector import HypnocubeConnection
from animations.color_sorting import ColorSorting
from animations.season_lights import *
from animations.cube_traversal import CubeTraversal


class DemoRunner:

    def __init__(self):
        parser = argparse.ArgumentParser(prog='hypnocube_demo')
        parser.add_argument('-p', metavar='portname', required=True, help='Name of the port that the hypnocube is connected on.  You can probably find the portname by doing ls /dev/cu.usb*')

        args = parser.parse_args()
        self.portname = args.p
        self.connection = HypnocubeConnection(self.portname)


    def color_sorting(self):
        animator = CubeAnimator(self.connection, ColorSorting(4))
        animator.run()

    def season_lights(self):
        light_show = SeasonLights.get_default_lights()
        animator = CubeAnimator(self.connection, light_show)
        animator.run()

    def cube_traversal(self):
        animator = CubeAnimator(self.connection, CubeTraversal(True))
        animator.run()

