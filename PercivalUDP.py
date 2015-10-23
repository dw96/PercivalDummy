'''
    PercivalUDP - Capture UDP traffic, extract and save to file (relevant parts of) the Percival payload
                    Loosely based upon PercivalReceive*.py
'''

import socket, time, sys, time
from select import select
from datetime import datetime

# Save data to RAM (& disk, once all data captured)
capturedData00 = ""
capturedData01 = ""
# ID each socket
SOCKET00 = 0
SOCKET01 = 1

def read_udp(sock, f, bFirstWrite, UDP_IP, UDP_PORT):

    global capturedData00, capturedData01, SOCKET00, SOCKET01   # Declare variables as global
    
    data, address = sock.recvfrom(8000)
    # Only print "header" info once to file
    if bFirstWrite:
        if f == SOCKET00:
            capturedData00 += "________________________________________\n"
            capturedData00 += ("From: %s targeting: %s:%d\n" % ( address, UDP_IP, UDP_PORT))
            headerInfo(f)
            capturedData00 += "________________________________________\n\n"
#             print " 1 read_udp() capturedData00:\n", capturedData00
        elif f == SOCKET01:
            capturedData01 += "________________________________________\n"
            capturedData01 += ("From: %s targeting: %s:%d\n" % ( address, UDP_IP, UDP_PORT))
            headerInfo(f)
            capturedData01 += "________________________________________\n\n"
#             print " 1 read_udp() capturedData01:\n", capturedData01
        else:
            print "Error: read_udp() fed unknown socket handle f = ", f, "\n\n"
            raise Exception

    # Convert data into hexadecimal string (more viewable)
    headerData = ''.join( [ "%02X " % ord( x ) for x in data [:22] ] ).strip()

    if f == SOCKET00:
        capturedData00 += ("%d   %s  %s  %s   (Src:%s)\n" % (UDP_PORT, headerData[:23], headerData[24:47], headerData[48:], address) )
#         print " 2 read_udp() capturedData00:\n", capturedData00 
    elif f == SOCKET01:
        capturedData01 += ("%d   %s  %s  %s   (Src:%s)\n" % (UDP_PORT, headerData[:23], headerData[24:47], headerData[48:], address) )
#         print " 2 read_udp() capturedData01:\n", capturedData01
    else:
        print "Error: read_udp() fed unknown socket handle f = ", f, "\n\n"
        raise Exception

    
def PercivalUDP(address, hostString):

    global capturedData00, capturedData01, SOCKET00, SOCKET01   # Declare variables as global
    
    UDP_PORTS = (8000, 8001)

    dateString = datetime.now().strftime("%Y%m%d-%H%M%S")
    fileName00 = "/tmp/Percy_%s_%s--%s.txt" % (str(hostString), str(UDP_PORTS[0]), dateString)
    f00 = open(fileName00, "w")
    
    # Repeat for second file handle
    fileName01 = "/tmp/Percy_%s_%s--%s.txt" % (str(hostString), str(UDP_PORTS[1]), dateString)
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
        print "Listening for incoming data.. [Capturing all packets]"
        while True:
            inputready,outputready,exceptready = select(input,[],[])

            for s in inputready:
                if s == udp00:
#                     print "udp00 - - - - - - - - - - - - - - - - - - - - - - - - -------------- - - - - - - - - - - - - - - - - - - - - - - - - --------------"; time.sleep(2)
                    sender = read_udp(s, SOCKET00, bFirstWrite0, address, UDP_PORTS[0])
                    bFirstWrite0 = False
#                     print len(capturedData00)
                elif s == udp01:
#                     print "udp01  - - - - - - - - - - - - - - - - - - - - - - - - -------------- - - - - - - - - - - - - - - - - - - - - - - - - --------------" ; time.sleep(2)
                    sender = read_udp(s, SOCKET01, bFirstWrite1, address, UDP_PORTS[1])
                    bFirstWrite1 = False
#                     print len(capturedData01)
                else:
                    print "unknown socket:", s
    except KeyboardInterrupt:
        print " *** User interrupted programme"
        print "Saving captured data to disk..", len(capturedData00), len(capturedData01)
        print >> f00, (capturedData00)
        print >> f01, capturedData01
        if not f00.closed:
            f00.close()
        if not f01.closed:
            f01.close()
    print "Created filename:\n%s\n%s" % (fileName00, fileName01)
            
def headerInfo(fHandle):
    ''' Display internal boundaries within the UDP header '''
    
    global capturedData00, capturedData01, SOCKET00, SOCKET01   # Declare variables as global
    if fHandle == SOCKET00:
        capturedData00 += "Src Port \n"
        capturedData00 += "|        PktType [1 Byte]\n"
        capturedData00 += "|        |  subframeNumber [1 Byte]\n"
        capturedData00 += "|        |     FrameNumber [4 Bytes]\n"
        capturedData00 += "|        |                 PacketNumber [2 Bytes]\n"
        capturedData00 += "|        |  |  |           |\n"
        capturedData00 += "|        |  |  |           |\n"
#         print " headerInfo() capturedData00:\n", capturedData00
    elif fHandle == SOCKET01:
        capturedData01 += "Src Port \n"
        capturedData01 += "|        PktType [1 Byte]\n"
        capturedData01 += "|        |  subframeNumber [1 Byte]\n"
        capturedData01 += "|        |     FrameNumber [4 Bytes]\n"
        capturedData01 += "|        |                 PacketNumber [2 Bytes]\n"
        capturedData01 += "|        |  |  |           |\n"
        capturedData01 += "|        |  |  |           |\n"
#         print " headerInfo() capturedData01:\n", capturedData01
    else:
        print "Error: headerInfo() fed unknown socket handle f = ", f, "\n\n"
        raise Exception

if __name__ == "__main__":
    # Test user specified (TCP ip) command line argument
    address = "10.1.0.1"
    try:
        address = sys.argv[1]
        if not "." in address:      # rudimentary sanity check
            raise Exception
        hostString = sys.argv[2]
        hostString = hostString.replace(" ", "") # Remove all white spaces
        hostString = hostString.strip()
        print "'%s'" % hostString
    except Exception:
        print "Invalid input(s); Correct Usage: "
        print "python PercivalUDP.py <address> <hostDescription> \n"
        print "e.g. ' python PercivalUDP.py 10.1.0.1 Node01'\n(Note: port numbers assumed: 8000 & 8001)\n"
    else:
        PercivalUDP(address, hostString)
