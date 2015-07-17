'''
    PercivalReceiveBrief - Capture UDP traffic, saving the first and last 10 packets of each subframe

Utilise this script from the Python command prompt:

from PercivalReceiveBrief import PercivalReceiveBrief
sock = PercivalReceiveBrief()
sock.close();del  PercivalReceiveBrief

'''
# Source (in part): https://wiki.python.org/moin/UdpCommunication
import socket, time, sys, numpy as np
from datetime import datetime
#        sys.stdout.flush()     # Flush stdout
#       Or start from the command line with: python -u
print "colour Roundup!"
def PercivalReceiveBrief():
    UDP_IP = "10.2.0.11"
    UDP_PORT = 8001

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.bind((UDP_IP, UDP_PORT))

    # Open and close dummy file
    fileName = "/tmp/no_such.file"
    f = open(fileName, "w")
    f.close()

    print "Idling.",
    (subframe, data, packetCounter) = (0, 0, 0)
    listFiles = []
    try:
        while True:
            # Receive UDP data, convert into unsigned 8-bit integer
            packetCounter += 1
            try:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                # Data received, open file handle if shut
                if f.closed:
                    dateString = datetime.now().strftime("%Y%m%d-%H%M%S")
                    fileName = "/tmp/Percy_headers-%s.txt" % ( dateString)
                    f = open(fileName, "w")
            except KeyboardInterrupt:
                # User killed function
                print "\n*** User initiated shutdown ***"
                for index in listFiles:
                    print "(Saved file %s) " % index
                if not f.closed:
                    print "Closing the file"
                    f.close()
                return sock
            except socket.timeout as e: # e = "timed out"
                # Close file handle (until data available again)
                if not f.closed:
                    listFiles.append(fileName)
                    f.close()
                    print "\nData received; Awaiting next to data.."
                else:
                    print ".",
                continue
                #
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
        print "Unsuspected error:", e

