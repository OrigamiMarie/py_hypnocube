import serial
import crc16
from command_code import CommandCode


class HypnocubeConnection():

    PAYLOAD_MAX_BYTES = 50


    def __init__(self, portName, baudrate):
        self.serial_connection = serial.Serial(port=portName, baudrate=baudrate,
                                               timeout=0.5)

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
        print "Sending packet:\n%s" % packet.pretty_string()
        self.serial_connection.write(str(bytearray(packet.packet)))
        result = self.read_all()
        print result
        #print packet.pretty_string_from_packet(bytearray(result))
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

    def packet_count(self, byte_count):
        # This will truncate (not round).  
        # That means we need to add one more byte, 
        # except in the case where the fit is just perfect.  
        count = byte_count / self.PAYLOAD_MAX_BYTES
        count = count if (byte_count % self.PAYLOAD_MAX_BYTES == 0) \
                      else count + 1
        return count

    def login(self):
        # This is a long, careful dance.  
        # Probably the most complicated command, and it's first.  
        packet1 = Packet.from_parts(True, 0, CommandCode.LOGIN, [])
        result_packets = self.send_packet_get_packets(packet1)
        print "number of returned packets:  %d" % len(result_packets)
        for p in result_packets:
            print p.checksum_valid
            if p.checksum_valid:
                print p.pretty_string()
            else:
                print p.pretty_string_from_packet(p.packet)





class Packet:

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
        p.payload_length = len(data) + 1
        p.pack_it()
        return p

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
        calculated_checksum = crc16.crc16xmodem(str(packet_list), 0xFFFF)
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
        # Fourth byte:  command.
        self.command = CommandCode.get_name(packet_list[3])
        # Fifth byte through current end:  data.
        self.data = packet_list[4:]


    def pack_it(self):
        # Start with a list because we have no idea about its eventual length.
        packet_list = []
        # First byte:
        # High 3 bits = last/not-last packet
        # Low 5 bits = packet sequence number
        packet_list.append(self.packet_type + self.sequence_number)
        # Second byte:  payload length (the command is an extra byte)
        packet_list.append(len(self.data) + 1)
        # Third byte:  destination.  
        # We're not going to the trouble of aiming this at a particular device.
        # Whoever's listening on the port gets this packet.
        packet_list.append(Packet.DESTINATION_BROADCAST)
        # Fourth byte:  command
        packet_list.append(CommandCode.get_number(self.command))
        # Starting at the fifth byte:  data
        packet_list.extend(self.data)
        # Last two bytes:  checksum for the message up through this point.
        checksum = crc16.crc16xmodem(str(packet_list), 0xFFFF)
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
                packet_list.insert(i+1)
                i = i + 1
            i = i + 1

    def pretty_packet_string(self):
        return self.pretty_string_from_packet(self.packet)

    def pretty_string_from_packet(self, packet):
        if packet is None:
            return "None"
        return [hex(b) for b in packet]



