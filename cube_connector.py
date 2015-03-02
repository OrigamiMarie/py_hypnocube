import serial
import crc16
import itertools
import random
from cube_model import *


class HypnocubeConnection:

    def __init__(self, portName, baudrate=40000, device_id=[0xAB, 0xAD, 0xC0, 0xDE], 
                 edge_length=4):
        """
        Initialization for the HypnocubeConnection
        This initializations opens the connection.  It seems wise to close the connection
        when done, but I haven't seen any ill effects from not doing so.  
        The cube automatically logs you out after a second or so of no communication.  

        portName is something like "/dev/cu.usbmodem1411"
        On *nix and OS X systems, do "ls /dev/*usb*" with hypnocube connected and turned on 
        in order to find out your particular port.  

        baudrate defaults to 40000.  The spec says 38400, but I've had better luck here.

        device_id will be the default unless you've specifically changed your device's id.

        edge_length defaults to 4 because there are only 4x4x4 cubes now.  
        """
        self.device_id = device_id
        self.edge_length = edge_length
        self.serial_connection = serial.Serial(port=portName, baudrate=baudrate,
                                               timeout=0.1)

    def close(self):
        """
        Closes the connection to the hypnocube.  
        """
        self.serial_connection.close()

    def _read_all(self):
        return self.serial_connection.read(10000)

    def _send_packet_get_packets(self, packet):
        self.serial_connection.write(str(bytearray(packet.packet)))
        result = self._read_all()
        packets = []
        while len(result) > 0 and result.find(_Packet.SYNC_CHAR) >= 0:
            result = result[result.find(_Packet.SYNC_CHAR):]
            if result.find(_Packet.SYNC_CHAR, 1) >= 0:
                split_point = result.find(_Packet.SYNC_CHAR, 1) + 1
                packet_string = result[:split_point]
                result = result[split_point:]
                packets.append(_Packet.from_wire(packet_string))
            else:
                # Make sure to empty out the string, otherwise that last SYNC
                # is going to keep the while going forever.
                result = ""
        return packets

    @staticmethod
    def _packets_to_cube_model(packets):
        # First concatenate all of the data into one list.
        data = []
        for packet in packets:
            data.extend(packet.data)
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
        cube = CubeModel(self.edge_length, 0)
        i = 0
        for x in xrange(0, self.edge_length):
            for y in xrange(0, self.edge_length):
                for z in xrange(0, self.edge_length):
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
    def _cube_model_to_byte_list(cube_model):
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
        """
        Send a CubeModel to the hypnocube and make it show on the cube.  
        """
        data = HypnocubeConnection._cube_model_to_byte_list(cube)
        packets = _Packet.packets_list_from_parts(_CommandCode.SET_FRAME, data)
        for packet in packets:
            result = self._send_packet_get_packets(packet)
        flip_packet = _Packet.from_parts(True, 0, _CommandCode.FLIP_FRAME, [])
        result = self._send_packet_get_packets(flip_packet)

    def get_cube_from_hypnocube(self, n):
        """
        Get the CubeModel of current colors from the hypnocube
        """
        packet = _Packet.from_parts(True, 0, _CommandCode.GET_FRAME, [])
        result_packets = self._send_packet_get_packets(packet)
        return HypnocubeConnection._packets_to_cube_model(result_packets, n)

    @staticmethod
    def _print_all_packets(packets):
        print "number of packets: %d" % len(packets)
        for p in packets:
            print p.checksum_valid
            if p.checksum_valid:
                print p.pretty_string()
            else:
                print p.pretty_string_from_packet(p.packet)



    def login(self):
        """
        You'll need to log in to the cube before doing anything interesting.  
        The cube logs you out if you don't send some kind of command every second or so.  
        The right command for that is ping, which we haven't implemented yet.  Sorry.  
        """
        packet1 = _Packet.packets_list_from_parts(_CommandCode.LOGIN, 
                                                 self.device_id)[0]
        result_packets = self._send_packet_get_packets(packet1)




class _Packet:

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
        p.packet_type = _Packet.PACKET_TYPE_LAST if is_last_packet \
                      else _Packet.PACKET_TYPE_NOT_LAST
        p.sequence_number = sequence_number
        p.command = command
        p.data = data
        p.payload_length = len(data) + 1 if sequence_number == 0 else len(data)
        p.pack_it()
        return p


    @staticmethod
    def packets_list_from_parts(command, data):
        data_list = _Packet.chunk_data(data)
        packet_count = len(data_list)
        last_packet = packet_count - 1
        packet_list = []
        for i in xrange(0, packet_count):
            packet_list.append(_Packet.from_parts(i==last_packet, 
                                                 i,
                                                 command,
                                                 data_list[i]))
        return packet_list


    @staticmethod
    def chunk_data(data):
        return [data [i:i + _Packet.DATA_MAX] 
                for i in xrange(0, len(data), _Packet.DATA_MAX)]


    def pretty_string(self):
        return "Type: %s, Seq: %s, Len: %d, Command: %s, Data:\n%s" % \
               (self.packet_type, self.sequence_number, self.payload_length,
                self.command, self.pretty_string_from_packet(self.data))


    def unpack_it(self):
        # The self.packet is either an immutable-length bytearray or 
        # an immutable string.  Either way, we want a list.  
        packet_list = list(self.packet)
        # Remove the SYNC bytes from either end, if they exist.
        if packet_list[0] == _Packet.SYNC:
            packet_list.pop(0)
        if packet_list[-1] == _Packet.SYNC:
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
        self.command = _CommandCode.NONE
        if self.sequence_number == 0:
            start_of_data = 4
            self.command = _CommandCode.get_name(packet_list[3])
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
        packet_list.append(_Packet.DESTINATION_BROADCAST)
        # Fourth byte:  command (but only if this is the first packet in seq)
        if self.sequence_number == 0:
            packet_list.append(_CommandCode.get_number(self.command))
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
        packet_list.insert(0, _Packet.SYNC)
        packet_list.append(_Packet.SYNC)
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
            if packet_list[i] == _Packet.ESC:
                if packet_list[i+1] == _Packet.ESC1:
                    # Remove both the ESC and ESC1, put a SYNC in their place.
                    packet_list.pop(i)
                    packet_list.pop(i)
                    packet_list.insert(i, _Packet.SYNC)
                elif packet_list[i+1] == _Packet.ESC2:
                    # Just take off the ESC2, leaving the ESC
                    packet_list.pop(i+1)
            i = i + 1

    # Instances of SYNC will be replaced with two bytes ESC, ESC1.  
    # Other instances of ESC will be replaced with two bytes ESC, ESC2.
    def escape_packet_list(self, packet_list):
        i = 0
        while i < len(packet_list):
            if packet_list[i] == _Packet.SYNC:
                packet_list.pop(i)
                # Adding in reverse order because inserting pushes forward
                packet_list.insert(i, _Packet.ESC1)
                packet_list.insert(i, _Packet.ESC)
                i = i + 1
            elif packet_list[i] == _Packet.ESC:
                packet_list.insert(i+1, _Packet.ESC2)
                i = i + 1
            i = i + 1

    def pretty_packet_string(self):
        return self.pretty_string_from_packet(self.packet)

    def pretty_string_from_packet(self, packet):
        if packet is None:
            return "None"
        return [hex(b) for b in packet]




class _CommandCode():

    # Ah . . . I'm kinda new here, and there's probably a much better way
    # to do this.  But this is the way that's obvious to me right now, 
    # so off we go!

    NONE = "NONE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    RESET = "RESET"
    INFO = "INFO"
    VERSION = "VERSION"
    OPTIONS = "OPTIONS"
    ERROR = "ERROR"
    GET_ERROR = "GET_ERROR"
    ACK = "ACK"
    CURRENT_ITEM = "CURRENT_ITEM"
    MAX_VIS_IDX = "MAX_VIS_IDX"
    SELECT_VIS = "SELECT_VIS"
    MAX_TRAN_IDX = "MAX_TRAN_IDX"
    SELECT_TRAN = "SELECT_TRAN"
    SET_RATE = "SET_RATE"
    PING = "PING"
    FLIP_FRAME = "FLIP_FRAME"
    SET_FRAME = "SET_FRAME"
    GET_FRAME = "GET_FRAME"
    SET_P_FRAME = "SET_P_FRAME"
    SET_PIXEL = "SET_PIXEL"
    GET_PIXEL = "GET_PIXEL"
    DRAW_LINE = "DRAW_LINE"
    DRAW_BOX = "DRAW_BOX"
    FILL_IMAGE = "FILL_IMAGE"
    SCROLL_TEXT = "SCROLL_TEXT"
    LOAD_ANIM = "LOAD_ANIM"

    forward_tuples = [(NONE, -1),
                      (LOGIN, 0), (LOGOUT, 1), (RESET, 10), (INFO, 11),
                      (VERSION, 12), (OPTIONS, 15), (ERROR, 20),
                      (GET_ERROR, 21), (ACK, 25), (CURRENT_ITEM, 30),
                      (MAX_VIS_IDX, 40), (SELECT_VIS, 41), (MAX_TRAN_IDX, 42),
                      (SELECT_TRAN, 43), (SET_RATE, 50), (PING, 60),
                      (FLIP_FRAME, 80), (SET_FRAME, 81), (GET_FRAME, 82),
                      (SET_P_FRAME, 83), (SET_PIXEL, 84), (GET_PIXEL, 85),
                      (DRAW_LINE, 85), (DRAW_BOX, 87), (FILL_IMAGE, 88),
                      (SCROLL_TEXT, 89), (LOAD_ANIM, 90)]

    backward_tuples = [(b, a) for a, b in forward_tuples]

    names_to_numbers_dict = dict(forward_tuples)
    numbers_to_names_dict = dict(backward_tuples)

    @staticmethod
    def get_number(name):
        return _CommandCode.names_to_numbers_dict.get(name)

    @staticmethod
    def get_name(number):
        return _CommandCode.numbers_to_names_dict.get(number)


