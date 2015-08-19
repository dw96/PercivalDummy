'''
    tcpServer - Capture TCP traffic, extract and display the payload
    
    Acting as TCP server
'''

import socket, time, sys, numpy as np

def tcpServer(address, tcpPort):
    TCP_IP   = address
    TCP_PORT = tcpPort

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Modified to act as a server  [bind, listen]
    try:
        sock.bind((TCP_IP, TCP_PORT))
        sock.listen(1)
    except Exception as e:
        print " *** tcpServer Socket setup error:", e
        
    data = ""
    try:
        print "Listening for client on %s:%d." % (TCP_IP, TCP_PORT)
        connection, client_address = sock.accept()

        while True:
            # Receive TCP data, convert into unsigned 8-bit integer
            data, addr = connection.recvfrom(36) #1024) # buffer size is 1024 bytes
            if not data:
                # Client has shut connection; Close connection & accept next
                connection.close()
                connection, client_address = sock.accept()
                continue

            if len(data) > 0:
                print "'%s' sent %d bytes:" % (addr, len(data))
                for index in range(len(data)):
                    if (index != 0) and (index % 16 == 0):
                        print ""
                    if (index % 8 == 0):
                        print "  ",
                    print format(ord(data[index]), "x").zfill(2),
                print ""

    except KeyboardInterrupt:
        print "\n*** User initiated shutdown (2) ***"
    except Exception as e:
        print "Encountered Error:", e

    # Close connection & socket
    connection.close()
    sock.close()
    return

if __name__ == "__main__":
    # Test user specified (TCP port) command line argument
    (address, port) = ("192.168.0.103", 4321)
    try:
        address = sys.argv[1]
        port    = int(sys.argv[2])
        if not (address.count(".") == 3):      # rudimentary sanity check
            raise Exception
    except Exception:
        print "Invalid input(s); Correct Usage: "
        print "python tcpServer.py <address> <TCPport>\n"
        print "e.g. ' python tcpServer.py 192.168.0.103 4321'\n"
    else:
        tcpServer(address, port)
