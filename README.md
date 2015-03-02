This is a python connector for the Hypnocube (www.hypnocube.com).  

I'm not very experienced at Python yet, so I haven't made the dependencies automatic for this package.  

To use it, you'll need to do these commands (possibly with sudo):

pip install pyserial

pip install crc16


The main entry points into this software are cube_connector.HypnocubeConnection and cube_animator.CubeAnimator.  
These both have in-file help system style documentation.  
There is an example of connecting to a hypnocube in example.py.  

I'm new to Python, so I welcome (polite) suggestions for improvement in this package.  
