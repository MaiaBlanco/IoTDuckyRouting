# scanner.py

import struct
import bluetooth._bluetooth as bl


class BLScanner(object):

    def __init__(self):
        # Open bluetooth socket
        try:
            self.sock = bl.hci_open_dev(0)
        except:
            print("Error accessing BL device")
            sys.exit(1)
        # Enable LE scan
        bl.hci_send_cmd(self.sock, 0x08, 0x000C,
                        struct.pack("<BB", 0x01, 0x00))
        # Create new filter
        ble_filter = bl.hci_filter_new()
        bl.hci_filter_all_events(ble_filter)
        bl.hci_filter_set_ptype(ble_filter, bl.HCI_EVENT_PKT)
        # Set socket options to enable filter
        self.sock.setsockopt(bl.SOL_HCI, bl.HCI_FILTER, ble_filter)

    def packet_to_str(self, packet):
        out_str = ""
        for uchar in packet:
            out_str += "{:02X}".format(struct.unpack("B", uchar)[0])
        return out_str

    def packet_to_int(self, packet):
        out_int = 0
        multiple = 256
        for uchar in packet:
            out_int += struct.unpack("B", uchar)[0] * multiple
            multiple = 1
        return out_int

    def scan_all(self):
        while True:
            packet = self.sock.recv(255)
            event, = struct.unpack("B", packet[1]);
            # Check for LE subevent
            if event == 0x3E:
                subevent, = struct.unpack("B", packet[3])
                packet = packet[4:]
                # Check for LE advertising report
                if subevent == 0x02:
                    UUID = self.packet_to_str(packet[-22:-6])
                    MAJOR = self.packet_to_int(packet[-6:-4])
                    MINOR = self.packet_to_int(packet[-4:-2])
                    TXPOWER = struct.unpack("b", packet[-2])[0]
                    RSSI = struct.unpack("b", packet[-1])[0]
                    yield([UUID, MAJOR, MINOR, TXPOWER, RSSI])

