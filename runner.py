import time
from cube_connector import HypnocubeConnection
from command_code import CommandCode



connection = HypnocubeConnection("/dev/cu.usbmodem1421", 40000)
connection.login()

#foo = connection.send_string_get_response(' ')
#print foo
connection.close()
#time.sleep(1)

