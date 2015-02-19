import serial
import crc16
import itertools
import random
from command_code import CommandCode
from cube_model import *


class HypnocubeConnection:


    def __init__(self, portName, baudrate):
        self.serial_connection = serial.Serial(port=portName, baudrate=baudrate,
                                               timeout=0.1)

    def close(self):
        self.serial_connection.close()

    def toggle_pause(self):
        self.serial_connection.write(' ')

    def read_all(self):
        return self.serial_connection.read(10000)

    def send_string_get_response(self, s):
        self.serial_connection.write(s)
        return self.read_all()

    def send_packet_get_packets(self, packet):
        self.serial_connection.write(str(bytearray(packet.packet)))
        result = self.read_all()
        packets = []
        while len(result) > 0 and result.find(Packet.SYNC_CHAR) >= 0:
            result = result[result.find(Packet.SYNC_CHAR):]
            if result.find(Packet.SYNC_CHAR, 1) >= 0:
                split_point = result.find(Packet.SYNC_CHAR, 1) + 1
                packet_string = result[:split_point]
                result = result[split_point:]
                packets.append(Packet.from_wire(packet_string))
            else:
                # Make sure to empty out the string, otherwise that last SYNC
                # is going to keep the while going forever.
                result = ""
        return packets

    @staticmethod
    def packets_to_cube_model(packets, n):
        # First concatenate all of the data into one list.
        data = []
        for packet in packets:
            data.extend(packet.data)
        HypnocubeConnection.print_all_packets(packets)
        print data
        # Split the data into half-bytes.  
        # This will make the color conversions oh so much easier.  
        half_bytes = []
        for byte in data:
            half_bytes.append(byte>>4)
            half_bytes.append(byte - (byte>>4<<4))
        # Then make those half bytes into a list of colors.  
        colors = []
        # Assuming an even number of colors, and thus len(data)%3 = 0
        for i in xrange(0, len(half_bytes)-2, 3):
            colors.append(Color(half_bytes[i], 
                                half_bytes[i+1], 
                                half_bytes[i+2]))

        # Now make a cube and fill in the colors
        cube = CubeModel(n, 0)
        i = 0
        for x in xrange(0, n):
            for y in xrange(0, n):
                for z in xrange(0, n):
                    cube.set_pixel(x, y, z, colors[i])
                    i = i + 1
                    if i == len(data):
                        # This means we've run out of bytes to put in the cube.
                        # Normally, this should happen at the very end.
                        # If not enough bytes came back for the cube, 
                        # it'll happen early.  
                        return cube
        # Just in case there were too many bytes, we also put a return here.
        return cube

    @staticmethod
    def cube_model_to_byte_list(cube_model):
        # Unroll the 3d array into a 1d list, in two passes.
        two_d = [i for l in cube_model.cube for i in l]
        o = [i for l in two_d for i in l]
        # Pair off the colors.  Two colors make three bytes this way:
        # 1r1g 1b2r 2g2b
        # This is all very elegant as long as there is an even number of colors.
        # In even-numbered-sided cubes, this is the case.  
        # I'm guessing the cubes will always have even-numbered sides.
        # Have fun, future self, with that 5x5x5 cube!  
        data = [[(o[i].r<<4) + (o[i].g), 
                 (o[i].b<<4) + (o[i+1].r),
                 (o[i+1].g<<4) + (o[i+1].b)]
                 for i in xrange(0, len(o), 2)]
        # That went and made a list of lists again, so flatten it to return.  
        return [i for l in data for i in l]


    def send_cube_to_hypnocube(self, cube):
        data = HypnocubeConnection.cube_model_to_byte_list(cube)
        packets = Packet.packets_list_from_parts(CommandCode.SET_FRAME, data)
        for packet in packets:
            result = self.send_packet_get_packets(packet)
        flip_packet = Packet.from_parts(True, 0, CommandCode.FLIP_FRAME, [])
        result = self.send_packet_get_packets(flip_packet)

    def get_cube_from_hypnocube(self, n):
        packet = Packet.from_parts(True, 0, CommandCode.GET_FRAME, [])
        result_packets = self.send_packet_get_packets(packet)
        return HypnocubeConnection.packets_to_cube_model(result_packets, n)

    @staticmethod
    def print_all_packets(packets):
        print "number of packets: %d" % len(packets)
        for p in packets:
            print p.checksum_valid
            if p.checksum_valid:
                print p.pretty_string()
            else:
                print p.pretty_string_from_packet(p.packet)



    def login(self):
        device_challenge = [0xAB, 0xAD, 0xC0, 0xDE]
        packet1 = Packet.packets_list_from_parts(CommandCode.LOGIN, 
                                                 device_challenge)[0]
        result_packets = self.send_packet_get_packets(packet1)




class Packet:

    # Sure, technically we could do 49 for the first packet
    # (first one is command) and 50 for all subsequent packets.  
    # But this is prettier and will probably change the packet count
    # approximately never.  
    DATA_MAX = 48
    PACKET_TYPE_NOT_LAST = 2<<5
    PACKET_TYPE_LAST = 3<<5
    DESTINATION_BROADCAST = 0
    SYNC = 0xC0
    SYNC_CHAR = chr(SYNC)
    ESC = 0xDB
    ESC1 = 0xDC
    ESC2 = 0xDD
        
    # packet arrives as a string
    @classmethod
    def from_wire(cls, packet):
        p = cls()
        p.packet = bytearray(packet)
        p.unpack_it()
        return p

    # packet is created from parts
    @classmethod
    def from_parts(cls, is_last_packet, sequence_number, command, data):
        p = cls()
        p.packet_type = Packet.PACKET_TYPE_LAST if is_last_packet \
                      else Packet.PACKET_TYPE_NOT_LAST
        p.sequence_number = sequence_number
        p.command = command
        p.data = data
        p.payload_length = len(data) + 1 if sequence_number == 0 else len(data)
        p.pack_it()
        return p


    @staticmethod
    def packets_list_from_parts(command, data):
        data_list = Packet.chunk_data(data)
        packet_count = len(data_list)
        last_packet = packet_count - 1
        packet_list = []
        for i in xrange(0, packet_count):
            packet_list.append(Packet.from_parts(i==last_packet, 
                                                 i,
                                                 command,
                                                 data_list[i]))
        return packet_list


    @staticmethod
    def chunk_data(data):
        return [data [i:i + Packet.DATA_MAX] 
                for i in xrange(0, len(data), Packet.DATA_MAX)]


    def pretty_string(self):
        return "Type: %s, Seq: %s, Len: %d, Command: %s, Data:\n%s" % \
               (self.packet_type, self.sequence_number, self.payload_length,
                self.command, self.pretty_string_from_packet(self.data))


    def unpack_it(self):
        # The self.packet is either an immutable-length bytearray or 
        # an immutable string.  Either way, we want a list.  
        packet_list = list(self.packet)
        # Remove the SYNC bytes from either end, if they exist.
        if packet_list[0] == Packet.SYNC:
            packet_list.pop(0)
        if packet_list[-1] == Packet.SYNC:
            packet_list.pop()
        # Packet is escaped, need to unescape it.
        self.unescape_packet_list(packet_list)
        # Strip the checksum off the end, reconsistute it.
        checksum = (packet_list[-2]<<8) + packet_list[-1]
        packet_list = packet_list[:-2]
        # Make sure the checksum is valid.
        calculated_checksum = crc16.crc16xmodem(str(bytearray(packet_list)), 0xFFFF)
        self.checksum_valid = calculated_checksum == checksum
        # Alright, now we're going to work from the beginning for a while.  
        # First byte:
        # High 3 bits = last/not-last packet (hopefully).
        self.packet_type = (packet_list[0]>>5<<5)
        # Low 5 bits = packet sequence number.
        self.sequence_number = packet_list[0] - self.packet_type
        # Second byte:  payload length
        self.payload_length = packet_list[1]
        # Third byte:  destination.  We don't care.  
        # Fourth byte can be one of two things:
        #   if this is packet 0 in the sequence, it's the command.  
        #   if it's any other packet, it's just the start of the data.  
        start_of_data = 3
        self.command = CommandCode.NONE
        if self.sequence_number == 0:
            start_of_data = 4
            self.command = CommandCode.get_name(packet_list[3])
        # Fifth byte through current end:  data.
        self.data = packet_list[start_of_data:]


    def pack_it(self):
        # Start with a list because we have no idea about its eventual length.
        packet_list = []
        # First byte:
        # High 3 bits = last/not-last packet
        # Low 5 bits = packet sequence number
        packet_list.append(self.packet_type + self.sequence_number)
        # Second byte:  payload length (the command is an extra byte)
        packet_list.append(self.payload_length)
        # Third byte:  destination.  
        # We're not going to the trouble of aiming this at a particular device.
        # Whoever's listening on the port gets this packet.
        packet_list.append(Packet.DESTINATION_BROADCAST)
        # Fourth byte:  command (but only if this is the first packet in seq)
        if self.sequence_number == 0:
            packet_list.append(CommandCode.get_number(self.command))
        # Starting at the fifth byte:  data
        packet_list.extend(self.data)
        # Last two bytes:  checksum for the message up through this point.
        checksum = crc16.crc16xmodem(str(bytearray(packet_list)), 0xFFFF)
        # Need to chunk the checksum into two bytes.  
        # High byte:  shift it to the right 8 bits, let the bottom fall off.
        high_byte = checksum>>8
        # Low byte:  multiply that high byte back up, take it off the top.
        low_byte = checksum - (high_byte<<8)
        packet_list.append(high_byte)
        packet_list.append(low_byte)
        # Need to escape the unallowed bytes while it's still a list.  
        self.escape_packet_list(packet_list)
        # Then add the SYNC bytes at the beginning and end.
        packet_list.insert(0, Packet.SYNC)
        packet_list.append(Packet.SYNC)
        # Packet should be a bytearray, not a list.
        self.packet = bytearray(packet_list)

    # The opposite of escape_packet_list (see below).  
    # Sequences of ESC, ESC1 will be replaced with SYNC.  
    # Sequences of ESC, ESC2 will be replaced with ESC.  
    def unescape_packet_list(self, packet_list):
        i = 0
        # We're looking for two-byte sequences to replace,
        # so those can't start in the last place.  
        while i < len(packet_list) - 1:
            if packet_list[i] == Packet.ESC:
                if packet_list[i+1] == Packet.ESC1:
                    # Remove both the ESC and ESC1, put a SYNC in their place.
                    packet_list.pop(i)
                    packet_list.pop(i)
                    packet_list.insert(i, Packet.SYNC)
                elif packet_list[i+1] == Packet.ESC2:
                    # Just take off the ESC2, leaving the ESC
                    packet_list.pop(i+1)
            i = i + 1

    # Instances of SYNC will be replaced with two bytes ESC, ESC1.  
    # Other instances of ESC will be replaced with two bytes ESC, ESC2.
    def escape_packet_list(self, packet_list):
        i = 0
        while i < len(packet_list):
            if packet_list[i] == Packet.SYNC:
                packet_list.pop(i)
                # Adding in reverse order because inserting pushes forward
                packet_list.insert(i, Packet.ESC1)
                packet_list.insert(i, Packet.ESC)
                i = i + 1
            elif packet_list[i] == Packet.ESC:
                packet_list.insert(i+1, Packet.ESC2)
                i = i + 1
            i = i + 1

    def pretty_packet_string(self):
        return self.pretty_string_from_packet(self.packet)

    def pretty_string_from_packet(self, packet):
        if packet is None:
            return "None"
        return [hex(b) for b in packet]



