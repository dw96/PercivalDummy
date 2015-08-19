'''
    PercivalReceiveTCP - Capture TCP traffic, extract and display the Percival payload
    
    Acting as TCP server
'''

import socket, time, sys, numpy as np
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
        print "PRT Socket setup error:", e
        
    (subframe, data, packetCounter) = (0, 0, 0)
    listFiles = []
    try:
        print "Listening for client on %s:%d." % (TCP_IP, TCP_PORT)
        connection, client_address = sock.accept()
        
        data, addr = connection.recvfrom(36) #1024) # buffer size is 1024 bytes

        npData = np.fromstring(data, dtype=np.uint8)
        if len(npData) > 0:
            print "Received %d bytes:" % len(npData)
            for index in range(len(npData)):
                if (index != 0) and (index % 16 == 0):
                    print ""
                if (index % 8 == 0):
                    print "  ",
                print "%02X" % npData[index],
            print ""
        # Close connection
        connection.close()
            
    except KeyboardInterrupt:
        print "\n*** User initiated shutdown (2) ***"
    except Exception as e:
        print "PRT Unsuspected error:", e
    else:
        print "Closing down socket and exiting. [Aware: Using numpy puts 0 at 0x30, etc..]"
    connection.close()
    sock.close()

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
        PercivalReceiveTCP(address, port)
