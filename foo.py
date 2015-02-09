import pyhypnolsd

my_hypnolsd = pyhypnolsd.hypnolsd.HypnoLSD("/dev/tty.usbmodem1421", baudrate=38400)
the_response = my_hypnolsd.send_command("?", override=True, print_it=True) 
my_hypnolsd.demo_off()

