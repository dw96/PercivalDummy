'''
Created on Jan 15, 2015 - Based upon LpdFemUdpProducer.py (author: tcn45)

@author: ckd27546
'''

import argparse
import numpy as np
import socket
import time

class PercivalUdpProducerError(Exception):
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return repr(self.msg)

class PercivalUdpProducer(object):
 
    # Define custom class for Percival header
    HeaderType = np.dtype([('PacketType', np.uint8), ('SubframeNumber', np.uint8), ('FrameNumber', np.uint32), ('PacketNumber', np.uint16), ('Information', np.uint8, 14) ])
    
    def __init__(self, host, port, frames, interval, display):
        
        self.host = host
        self.port = port
        self.frames = frames
        self.interval = interval
        self.display = display
        
        # Initialise shape of data arrays in terms of sections and pixels
        # 1 quarter     = 704 x 742 pixels (columns x rows)
        self.quarterRows = 2
        self.quarterCols = 1        # 2
        self.colBlocksPerQuarter = 22
        self.colsPerColBlock     = 32
        self.rowBlocksPerQuarter = 106
        self.rowsPerRowBlock     = 7
        
        self.numPixelRows = self.quarterRows * self.rowBlocksPerQuarter * self.rowsPerRowBlock
        self.numPixelCols = self.quarterCols * self.colBlocksPerQuarter * self.colsPerColBlock
        self.numPixels    = self.numPixelRows * self.numPixelCols
        
        # Initialise an array representing a single image in the system
        self.imageArray = np.empty((self.numPixelRows * self.numPixelCols), dtype=np.uint16)
        self.resetArray = np.ones((self.numPixelRows * self.numPixelCols), dtype=np.uint16)
        # Fill in image array with ..

        pixelValue = 0
        
        for subframe in range(1):   #2):
            for row in range(self.rowBlocksPerQuarter * 2): # 106 * 2 = 212
                for column in range(self.colBlocksPerQuarter):
                    for adc in range(224):          # = self.rowsPerRowBlock * self.colBlocksPerQuarter ? (7 * 32 = 224)
                        
                        index = (subframe * self.numPixels) + (row * 4928) + (column * 224) + adc
                        
                        self.imageArray[index] = adc # (adc << 2)  #TODO: Bit shift 2 steps; include B1B0 2 LSBs, Coarse bits 6 MSBs

                        #self.resetArray[index] = 1  #TODO: Bit shift 2 steps, include B1B0 2 LSBs, Coarse bits 6 MSBs

        # Convert data stream to byte stream for transmission
        self.byteStream = self.imageArray.tostring()

        
        
    def run(self):
        
        self.payloadLen = 8192
        startOfFrame    = 0#x80000000
        endOfFrame      = 0#x40000000
        self.bytesPerPixels      = 2
        self.subframeSize        = self.numPixels * self.bytesPerPixels

        print "Starting Percival data transmission to address", self.host, "port", self.port, "..."
                
        # Open UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create packet header
        header = np.zeros(1, dtype=self.HeaderType)
        
        # Load header with dummy values
        header['PacketType']        = 85   # Packet Type        (1 Byte)     [85 = 0x55]
        header['SubframeNumber']    = 171   # Subframe Number    (1 Byte)    [171 = 0xAB]
        header['FrameNumber']       = 0xA0000A   # Frame Number       (4 Bytes)    
        header['PacketNumber']      = 0   # Packet Number      (2 Bytes)
        header['Information']       = 0   # Information        (14 Bytes)
        
        totalBytesSent = 0
        runStartTime = time.time()
        
        print "debug: bytes to send: ", len(self.byteStream), "versus subframeSize: ", self.subframeSize
        print "debug: size of header: ", len(header.tostring()) # 22 Bytes
        for frame in range(self.frames):
            
            bytesRemaining = len(self.byteStream) 
            
            streamPosn = 0
            subframeCounter = 0
            packetCounter = 0
            bytesSent = 0
            subframeTotal = 0       # Count how much of the current subframe has been sent

            frameStartTime = time.time()

            while bytesRemaining > 0:
                
                # Calculate packet size and construct header

                if bytesRemaining <= self.payloadLen:
                    bytesToSend = bytesRemaining
                    header['PacketNumber'] = packetCounter | endOfFrame

                else:
                    # Will current payload span 2 subframes?
                    subframeRemainder = self.subframeSize - subframeTotal

                    if (subframeRemainder < self.payloadLen):
                        bytesToSend = subframeRemainder
                    else:
                        bytesToSend = self.payloadLen
                    header['PacketNumber'] = packetCounter | startOfFrame if packetCounter == 0 else packetCounter
                
                header['SubframeNumber'] = subframeCounter
                header['FrameNumber'] = frame
                subframeTotal += bytesToSend
                if subframeTotal >= self.subframeSize:
                    subframeTotal = 0
                    subframeCounter += 1
                
                # Append header to current packet
                packet = header.tostring() + self.byteStream[streamPosn:streamPosn+bytesToSend]

                # Transmit packet
                bytesSent += sock.sendto(packet, (self.host, self.port))
                
                # DEBUG
                #print "Pkt: %3d bytesSent: %7d (0x%6X) bytesRemaining: %7d (0x%6X)" % (packetCounter, bytesSent,  bytesSent, bytesRemaining, bytesRemaining)

                bytesRemaining -= bytesToSend
                streamPosn += bytesToSend
                packetCounter += 1
                 
            print "  Sent frame", frame, "packets", packetCounter, "subframes", subframeCounter, "bytes", bytesSent
            totalBytesSent += bytesSent

            # Calculate wait time and sleep so that frames are sent at requested intervals            
            frameEndTime = time.time()
            waitTime = (frameStartTime + self.interval) - frameEndTime
            if waitTime > 0:
                time.sleep(waitTime)
       
        runTime = time.time() - runStartTime
             
        # Close socket
        sock.close()
        
        print "%d frames completed, %d bytes sent in %.3f secs" % (self.frames, totalBytesSent, runTime)
        
        if self.display:
            self.displayImage()
            
    def displayImage(self):

        import matplotlib.pyplot as plt
 
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        img = ax.imshow(self.imageArray)
        plt.show()       
        
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="PercivalUdpProducer - generate a simulated LPD FEM UDP data stream")
    
    parser.add_argument('--host', type=str, default='127.0.0.1', 
                        help="select destination host IP address")
    parser.add_argument('--port', type=int, default=61649,
                        help='select destination host IP port')
    parser.add_argument('--frames', '-n', type=int, default= 0, #1,
                        help='select number of frames to transmit')
    parser.add_argument('--interval', '-t', type=float, default=0.1,
                        help="select frame interval in seconds")
    parser.add_argument('--display', "-d", action='store_true',
                        help="Enable diagnostic display of generated image")
    
    args = parser.parse_args()

    producer = PercivalUdpProducer(**vars(args))
    producer.run()
    # PercivalDummy
