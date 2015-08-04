'''
    PercivalReceiveTCP - Capture TCP traffic, extract and display the Percival TCP headers from payload
'''

import socket, time, sys, numpy as np
# from datetime import datetime
#        sys.stdout.flush()     # Flush stdout
#       Or start from the command line with: python -u

def PercivalReceiveTCP(address, udpPort):
    TCP_IP   = address    # "192.168.0.103"
    TCP_PORT = udpPort    # 4321

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Modified to act as a server  [bind, listen]
    try:
        sock.bind((TCP_IP, TCP_PORT))
        sock.listen(1)
    except Exception as e:
        print "Socket setup error:", e
        
    (subframe, data, packetCounter) = (0, 0, 0)
    listFiles = []
    try:
        print "Listening for client on %s:%d." % (TCP_IP, TCP_PORT)
        connection, client_address = sock.accept()
        
        while True:
            # Receive TCP data, convert into unsigned 8-bit integer
            packetCounter += 1
            try:
                
                data, addr = connection.recvfrom(1024) # buffer size is 1024 bytes
                # data contains number of bytes
                if packetCounter == 1:
                    print "Data received!\n"
                    sys.stdout.flush()
                                 
            except KeyboardInterrupt:
                print "\n*** User initiated shutdown ***"
                return

            npData = np.fromstring(data, dtype='uint8')
            if len(npData) > 0:
                print "Converted data into %d bytes." % len(npData)
                for index in range(len(npData)):
                    if (index != 0) and (index % 16 == 0):
                        print ""
                    if (index % 8 == 0):
                        print "  ",
                    print "%02X" % npData[index],
                print ""

#                 print " npData:\n", npData, "\n--------------------------"
    
    except KeyboardInterrupt:
        print "\n*** User initiated shutdown ***"
        return
    except Exception as e:
        print "Unsuspected error:", e


if __name__ == "__main__":
    # Test user specified (TCP port) command line argument
    (address, port) = ("10.2.0.11", 8000)
    try:
        address = sys.argv[1]
        port    = int(sys.argv[2])
        if not "." in address:      # rudimentary sanity check
            raise Exception
    except Exception:
        print "Invalid input(s); Correct Usage: "
        print "python PercivalReceiveTCP.py <address> <TCPport>\n"
        print "e.g. ' python PercivalReceiveTCP.py 10.2.0.1 8000'\n"
    else:
        #print "Configured to listen on address:",  address, "port", port
        PercivalReceiveTCP(address, port)
