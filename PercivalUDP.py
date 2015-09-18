'''
    PercivalUDP - Capture UDP traffic, extract and save to file (relevant parts of) the Percival payload
                    Loosely based upon PercivalReceive*.py
'''

import socket, time, sys, numpy as np
import threading
from datetime import datetime

def PercivalUDP(address):
    UDP_IP   = address    # "10.1.0.1"
    UDP_PORTS= (8000, 8001)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(60)
        
    # Chop off the rest in a separate function, 1 thread for each port
    #   Whichever threading.Thread(..) Comes first, is executed first..
    lr = threading.Thread(target=listenForData(sock, UDP_IP, UDP_PORTS[1]))
    ld = threading.Thread(target=listenForData(sock, UDP_IP, UDP_PORTS[0]))
    ld.start()
    lr.start() 
    
    #TODO: Need to consider select that select to avoid one  sock.recv() blocking the other thread...?
    
def listenForData(sock, UDP_IP, UDP_PORT):
    
    print "Instance (attempting) listening to: [%s:%d]" % (UDP_IP, UDP_PORT)
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print UDP_PORT, "PRT Socket [%s:%d] Setup error:" % (UDP_IP, UDP_PORT), e

    # Open and close dummy file
    fileName = "/tmp/no_such.file"
    f = open(fileName, "w")
    f.close()

    print UDP_PORT, "Listening to %s:%d." % (UDP_IP, UDP_PORT)
    time.sleep(0.1)
    (subframe, data, packetCounter) = (0, 0, 0)
    listFiles = []
    try:
        while True:
            # Receive UDP data, convert into unsigned 8-bit integer
            packetCounter += 1
            try:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                if packetCounter == 1:
                    print UDP_PORT, "Data received!\n"
                    sys.stdout.flush()
                # Data received, open file handle if shut
                if f.closed:
                    dateString = datetime.now().strftime("%Y%m%d-%H%M%S")
                    fileName = "/tmp/Percy_headers_Port_%s-%s.txt" % (str(UDP_PORT), dateString)
                    f = open(fileName, "w")
                    print >> f, "________________________________________"
                    print >> f, ("Target: %s:%d\n" % (UDP_IP, UDP_PORT))
                    headerInfo(f)
                    print >> f, "________________________________________\n"
                    try:
                        sock.settimeout(3)
                    except Exception as e:
                        print UDP_PORT, "Couldn't reduce socket timeout: %s" % e
                        #print "PRT Socket [%s:%d] Setup error:" % (UDP_IP, UDP_PORT), e
                        return

            except socket.timeout as e: # e = "timed out"
                # Close file handle (until data available again)
                if not f.closed:
                    listFiles.append(fileName)
                    f.close()
                    print UDP_PORT, "Data received; Awaiting next data.."
                    sys.stdout.flush()
                else:
                    print UDP_PORT, ".",
                    sys.stdout.flush()

                print UDP_PORT, "No data after waiting 10 seconds; Closing down.."
                for index in listFiles:
                    print UDP_PORT, "(Saved file %s) " % index
                break

            npData = np.fromstring(data[:23], dtype='uint8')
            # Only display first & last packets of each subframe
            if (npData[7] < 10) or (npData[7] > 245):
                if npData[7] == 0:
                    print >> f, ("\npktNum:%i" % packetCounter)
                # Display 22 byte header of each packet
                for index in range(22):
                    if index % 8 == 0:
                        print >> f, "  ",
                    print >> f, ("%02X" % npData[index]),
                #
                print >> f, ""
    except Exception as e:
        print UDP_PORT, "Unsuspected error:", e


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
