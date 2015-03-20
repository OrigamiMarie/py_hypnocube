This is a python connector for the Hypnocube (www.hypnocube.com).  
It is not fully-featured.  


----- Getting Started -----

Sorry, I haven't figured out how to do all this with Windows yet.  My instructions apply to OS X and Ubuntu (and probably other flavors of Linux, I haven't tried them out but you can probably blunder along and work it out).  

*  You will need Python version 2 (not 3).  
*  You will also need pip.  If you're running Python >= 2.7.9, it's already installed.  If you're running an earlier version of Python, follow the instructions here https://pip.pypa.io/en/latest/installing.html
*  You will need virtualenv.  Once you've installed pip, this should be a simple matter of running "pip install virtualenv" (you may instead need "sudo pip install virtualenv").  

1.  It's best to set up a virtualenv, so that whatever terrible packages I decide to use don't conflict with any Python that you are already running (or may run in the future).  So, get a terminal running, and run these commands (parenthetical comments are not part of the commands):
*  mkdir hypnocube-virtualenv (dedicated directory for this virtualenv)
*  cd hypnocube-virtualenv (get into that directory)
*  virtualenv . (tell virtualenv that we want a virtualenv here)
*  source bin/activate (make use of this virtualenv.  This step will make your command line look a little weird, and you'll want to use a fresh terminal for any other work.  If you want to run this hypnocube stuff again, you only need to repeat getting into this directory and running this command.  The previous setup commands were one-time-only)

2.  Now to actually get the hypnocube software.  
pip install hypnocube

3.  Plug in your hypnocube if you haven't already.  Turn it on, and either use the B switch to get past the check sequences, or wait them out.  

4.  Now you need to figure out the port for your hypnocube.  Here are some possibilities:
-- OS X --
*  ls -la /dev/cu.usb* (this should give you a file name that is the port name)
-- Ubuntu (and possibly other *nix systems, I have't playe with them yet) --
*  ls -la /dev/serial (this will hopefully be a directory)
If that was a directory, it might have two directoies in it, by-id and by-path.  Do this (doesn't actually matter which directory):
*  ls -la /dev/serial/by-id
That should display some symlinks.  At the end of them, they will hopefully say something like ../../ttyACM0 .  
*  ls -la /dev/ttypACM0 (or whatever the tty thing was for you)
You'll probably see that it's owned by root, and in group dialout.  You're likely not in group dialout yet, and that will have to change if you want to connect to the hypnocube.  That gets just a little bit annoying . . . 
*  sudo usermod -a -G dialout <username> (without the <>, of course.  This adds you to the dialout group.  You can check success on that by doing groups <username> and you should see dialout amongst them)
Now you'll have to log out and log in again.  Sorry.  Just opening a new terminal won't help.  Now, get a new terminal, and get back to where you were.  

5.  Actually run a demo!  
In the directory, do this:
*  bin/hynocube_sorting_demo -p <portname> (with luck, your cube will fill with colors which will slowly swap with each other)



----- For Programmers -----

The main entry points into this software are cube_connector.HypnocubeConnection and cube_animator.CubeAnimator.  
These both have in-file help system style documentation.  
There is an example of connecting to a hypnocube in example.py.  

I'm new to Python, so I welcome (polite) suggestions for improvement in this package.  

