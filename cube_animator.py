import time
from cube_connector import HypnocubeConnection
from cube_model import CubeModel

class CubeAnimator:

    def __init__(self, connection, cube_generator):
        self.connection = connection
        self.cube_generator = cube_generator

    def run(self):
        for cube in self.cube_generator.next_cube():
            self.connection.send_cube_to_hypnocube(cube)
            time.sleep(cube.duration)


