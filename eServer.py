import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = sys.argv[1]
server_address = (server_name, 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
try:
    sock.bind(server_address)
    sock.listen(1)
except KeyboardInterrupt:
    print " User  interruption, exiting."
    sys.exit(1)

while True:
    print >>sys.stderr, 'waiting for a connection'
    try:
        connection, client_address = sock.accept()
        print >>sys.stderr, 'client connected:', client_address
        while True:
            data = connection.recv(1024)
            print >>sys.stderr, 'received "%s"' % data
            if data > 0:
                connection.sendall(data)
            else:
                break
    except KeyboardInterrupt:
        print " User  interruption, exiting."
    finally:
        connection.close()
