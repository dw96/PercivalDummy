'''
    PercivalUDP - Capture UDP traffic, extract and save to file (relevant parts of) the Percival payload
                    Loosely based upon PercivalReceive*.py
'''

import socket, time, sys, numpy as np
from select import select
from datetime import datetime

def read_udp(sock, f, bFirstWrite, UDP_IP, UDP_PORT):

    data, address = sock.recvfrom(8000)
    # Only print "header" info once to file
    if bFirstWrite:
        print >> f, "________________________________________"
        print >> f, ("From: %s targeting: %s:%d\n" % ( address, UDP_IP, UDP_PORT))
        headerInfo(f)
        print >> f, "________________________________________\n"
    
    packetCounter = 0
    # Extract Percival header from packet's payload
    npData = np.fromstring(data[:23], dtype='uint8')
    # Only want first & last packets of each subframe
    if (npData[7] < 10) or (npData[7] > 245):
        if npData[7] == 0:
            print >> f, ("\npktNum:%i (unchanged)" % packetCounter)
        # 22 byte header of each packet
        for index in range(22):
            if index % 8 == 0:
                print >> f, "  ",
            print >> f, ("%02X" % npData[index]),
        #
        print >> f, ""
    
def PercivalUDP(address):

    UDP_PORTS = (8000, 8001)

    dateString = datetime.now().strftime("%Y%m%d-%H%M%S")
    fileName00 = "/tmp/Percy__%s--%s.txt" % (str(UDP_PORTS[0]), dateString)
    f00 = open(fileName00, "w")
    
    # Repeat for second file handle
    fileName01 = "/tmp/Percy__%s--%s.txt" % (str(UDP_PORTS[1]), dateString)
    f01 = open(fileName01, "w")
    
    # create udp socket - port 8000
    udp00 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp00.bind((address,UDP_PORTS[0]))

    # create udp socket - port 8001
    udp01 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp01.bind((address,UDP_PORTS[1]))

    input = [udp00,udp01]

    (bFirstWrite0, bFirstWrite1)  = (True, True)
    try:
        print "Listening for incoming data.."
        while True:
            inputready,outputready,exceptready = select(input,[],[])

            for s in inputready:
                if s == udp00:
#                     print "udp00"
#                     time.sleep(1)
                    sender = read_udp(s, f00, bFirstWrite0, address, UDP_PORTS[0])
                    bFirstWrite0 = False
                elif s == udp01:
#                     print "udp01"
#                     time.sleep(1)
                    sender = read_udp(s, f01, bFirstWrite1, address, UDP_PORTS[1])
                    bFirstWrite1 = False
                else:
                    print "unknown socket:", s
    except KeyboardInterrupt:
        print " *** User interrupted programme"
        if not f00.closed:
            f00.close()
        if not f01.closed:
            f01.close()
    print "Created filenames:\n '%s'\n '%s'" % (fileName00, fileName01)
            
def headerInfo(fHandle):
    ''' Display internal boundaries within the UDP header '''
    print >> fHandle, "   PktType [1 Byte]"
    print >> fHandle, "      subframeNumber [1 Byte]"
    print >> fHandle, "         FrameNumber [4 Bytes]"
    print >> fHandle, "                     PacketNumber [2 Bytes]"
    print >> fHandle, "   |  |  |           |"
    print >> fHandle, "   |  |  |           |"

if __name__ == "__main__":
    # Test user specified (TCP ip) command line argument
    address = "10.1.0.1"
    try:
        address = sys.argv[1]
        if not "." in address:      # rudimentary sanity check
            raise Exception
    except Exception:
        print "Invalid input(s); Correct Usage: "
        print "python PercivalUDP.py <address> \n"
        print "e.g. ' python PercivalUDP.py 10.1.0.1'\n(Note: port numbers assumed: 8000 & 8001)\n"
    else:
        PercivalUDP(address)
