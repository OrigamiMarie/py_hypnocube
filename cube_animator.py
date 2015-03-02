import time
from cube_connector import HypnocubeConnection
from cube_model import CubeModel

class CubeAnimator:

    def __init__(self, connection, cube_generator):
        """
        Initializer for CubeAnimator

        connection is a HypnocubeConnection, and it does not need to be logged in.  

        cube_generator is an object that has a method called next_cube, 
        which generates CubeModels.   
        """
        self.connection = connection
        self.cube_generator = cube_generator

    def run(self):
        self.connection.login()
        for cube in self.cube_generator.next_cube():
            self.connection.send_cube_to_hypnocube(cube)
            time.sleep(cube.duration)


