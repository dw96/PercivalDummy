'''
    PercivalReceiveBrief - Capture UDP traffic, extract the Percival UDP headers, saving the first and last 10 packets of each subframe
'''
# Source (in part): https://wiki.python.org/moin/UdpCommunication
import socket, time, sys, numpy as np
from datetime import datetime
#        sys.stdout.flush()     # Flush stdout
#       Or start from the command line with: python -u

def PercivalReceiveBrief(address, udpPort):
    UDP_IP = address      #"10.2.0.11"
    UDP_PORT = udpPort    #8001

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(100) #5)
    sock.bind((UDP_IP, UDP_PORT))

    # Open and close dummy file
    fileName = "/tmp/no_such.file"
    f = open(fileName, "w")
    f.close()

    print "Listening to %s:%d." % (UDP_IP, UDP_PORT)
    (subframe, data, packetCounter) = (0, 0, 0)
    listFiles = []
    try:
        while True:
            # Receive UDP data, convert into unsigned 8-bit integer
            packetCounter += 1
            try:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                if packetCounter == 1:
                    print "Data received!\n"
                    sys.stdout.flush()
                # Data received, open file handle if shut
                if f.closed:
                    dateString = datetime.now().strftime("%Y%m%d-%H%M%S")
                    fileName = "/tmp/Percy_headers-%d-%s.txt" % (UDP_PORT, dateString)
                    f = open(fileName, "w")
                    print >> f, "________________________________________"
                    print >> f, ("Target: %s:%d\n" % (UDP_IP, UDP_PORT))
                    headerInfo(f)
                    print >> f, "________________________________________\n"
                    try:
                        sock.settimeout(3)
                    except Exception as e:
                        print "Couldn't reduce socket timeout: %s" % e
                        return
                                 
            except KeyboardInterrupt:
                # User killed function
                print "\n*** User initiated shutdown ***"
                if not f.closed:
                    #print "Closing the file %." %  fileName
                    listFiles.append(fileName)
                    f.close()
                for index in listFiles:
                    print "(Saved file %s) " % index
                return
            except socket.timeout as e: # e = "timed out"
                # Close file handle (until data available again)
                if not f.closed:
                    listFiles.append(fileName)
                    f.close()
                    print "\nData received; Awaiting next data.."
                    sys.stdout.flush()
                else:
                    print ".",
                    sys.stdout.flush()
                #continue
                print "No data after waiting 10 seconds;Closing down.."
                for index in listFiles:
                    print "(Saved file %s) " % index
                break
                #
            npData = np.fromstring(data[:24], dtype='uint8')
            # Only display first & last packets of each subframe
            if (npData[7] < 10) or (npData[7] > 245):
                # Display 22 byte header of each packet
                for index in range(24):
                    if index % 8 == 0:
                        print >> f, "  ",
                    print >> f, ("%02X" % npData[index]),
                #
                print >> f, ""
    except Exception as e:
        print "Unsuspected error:", e

def headerInfo(fHandle):
    ''' Display internal boundaries within the UDP header '''
    print >> fHandle, "   PxlData [2 Byte]"
    print >> fHandle, "         PktType [1 Byte]"
    print >> fHandle, "   |        subframeNumber [1 Byte]"
    print >> fHandle, "   |     |     FrameNumber [4 Bytes]"
    print >> fHandle, "   |     |  |                 PacketNumber [2 Bytes]"
    print >> fHandle, "   |     |  |  |                    PacketOffset [2 Bytes]"
    print >> fHandle, "   |     |  |  |              |           Information [12 Bytes]"
    print >> fHandle, "   |     |  |  |              |     |     |"
    print >> fHandle, "   |     |  |  |              |     |     |"


if __name__ == "__main__":
    # Test user specified (UDP port) command line argument
    (address, port) = ("10.2.0.11", 8000)
    try:
        address = sys.argv[1]
        port    = int(sys.argv[2])
        if not "." in address:      # rudimentary sanity check
            raise Exception
    except Exception:
        print "Invalid input(s); Correct Usage: "
        print "python PercivalReceiveBrief.py <address> <UDPport>\n"
        print "e.g. ' python PercivalReceiveBrief.py 10.2.0.1 8000'\n"
    else:
        #print "Configured to listen on address:",  address, "port", port
        PercivalReceiveBrief(address, port)
