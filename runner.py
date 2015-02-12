import time
from cube_connector import HypnocubeConnection
from command_code import CommandCode
from cube_animator import CubeAnimator
from animations.random_animation import RandomAnimation
from animations.gradual_scramble import GradualScramble


connection = HypnocubeConnection("/dev/cu.usbmodem1421", 40000)
connection.login()
animator = CubeAnimator(connection, GradualScramble())
animator.run()
#while 1==1:
#    connection.hacky_thing()
#    time.sleep(1)

#foo = connection.send_string_get_response(' ')
#print foo
connection.close()
#time.sleep(1)

