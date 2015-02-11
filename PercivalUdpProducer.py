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
        self.quarterCols = 2        # 2
        self.colBlocksPerQuarter = 22
        self.colsPerColBlock     = 32
        self.rowBlocksPerQuarter = 106
        self.rowsPerRowBlock     = 7
        
        self.numPixelRows   = self.quarterRows * self.rowBlocksPerQuarter * self.rowsPerRowBlock
        self.numPixelCols   = self.quarterCols * self.colBlocksPerQuarter * self.colsPerColBlock
        self.subframePixels = self.numPixelRows * self.numPixelCols / 2
        
        # Initialise an array representing a single image in the system
        self.imageArray = np.empty((self.numPixelRows * self.numPixelCols), dtype=np.uint16)
        self.resetArray = np.ones((self.numPixelRows * self.numPixelCols), dtype=np.uint16)

        self.numADCs = 224
        
        B0B1        = 0     # Which of the 4 horizontal regions does data come from?
        coarseValue = 0     # Which LVDS pair does data belong to?
        
        # Fill in image array with data according to emulator specifications
        for subframe in range(2):
            B0B1 = 0

            for row in range(self.rowBlocksPerQuarter * self.quarterRows): # 106 * 2 = 212

                if (row % 53 == 0) and (row != 0):
                    B0B1 += 1
            
                for column in range(self.colBlocksPerQuarter):
                
                    for adc in range(self.numADCs):          # 224
                        
                        if (adc % 32 == 0) and (adc != 0):
                            coarseValue += 1
                            if coarseValue == 32:
                                coarseValue = 0
                                
                        index = (subframe * self.subframePixels) + (row * 4928) + (column * 224) + adc
                        
                        self.imageArray[index] = (coarseValue << 10) + (adc << 2) + B0B1 
                        self.resetArray[index] = (coarseValue << 10) + (1 << 2) + B0B1

        # Convert data stream to byte stream for transmission
        self.imageStream = self.imageArray.tostring()
        self.resetStream = self.resetArray.tostring()
        
        
    def run(self):
        
        self.payloadLen     = 8192
        startOfFrame        = 0#x80000000
        endOfFrame          = 0#x40000000
        self.bytesPerPixels = 2
        self.subframeSize   = self.subframePixels * self.bytesPerPixels

        print "Starting Percival data transmission to address", self.host, "port", self.port, "..."
                
        # Open UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create packet header
        header = np.zeros(1, dtype=self.HeaderType)
        
        # Load header with dummy values
        header['PacketType']        = 85  # Packet Type        (1 Byte)     [85 = 0x55]
        header['SubframeNumber']    = 0   # Subframe Number    (1 Byte)
        header['FrameNumber']       = 0   # Frame Number       (4 Bytes)    
        header['PacketNumber']      = 0   # Packet Number      (2 Bytes)
        header['Information']       = 0   # Information        (14 Bytes)
        
        totalBytesSent = 0
        runStartTime = time.time()
        
        for frame in range(self.frames):
            
            print "frame: ", frame
            ######## Transmit Image Frame ########

            bytesRemaining = len(self.imageStream) 
            
            streamPosn      = 0
            subframeCounter = 0
            packetCounter   = 0
            bytesSent       = 0
            subframeTotal   = 0       # How much of current subframe has been sent

            frameStartTime = time.time()

            while bytesRemaining > 0:
                
                # Calculate packet size and construct header

                if bytesRemaining <= self.payloadLen:
                    bytesToSend = bytesRemaining
                    header['PacketNumber'] = packetCounter | endOfFrame

                else:
                    
                    subframeRemainder = self.subframeSize - subframeTotal
                    # Would sending full payload contain data from next subframe?
                    if (subframeRemainder < self.payloadLen):
                        bytesToSend = subframeRemainder
                    else:
                        bytesToSend = self.payloadLen
                    header['PacketNumber'] = packetCounter | startOfFrame if packetCounter == 0 else packetCounter
                
                header['SubframeNumber'] = subframeCounter
                header['FrameNumber']    = frame
                    
                # Prepend header to current packet
                packet = header.tostring() + self.imageStream[streamPosn:streamPosn+bytesToSend]

                # Transmit packet
                bytesSent += sock.sendto(packet, (self.host, self.port))

                bytesRemaining  -= bytesToSend
                streamPosn      += bytesToSend
                packetCounter   += 1
                subframeTotal   += bytesToSend

                if subframeTotal >= self.subframeSize:
                    print "  Sent Image frame:", frame, "subframe:", subframeCounter, "packets:", packetCounter, "bytes:", bytesSent
                    subframeTotal   = 0
                    subframeCounter += 1
                    packetCounter   = 0
                    totalBytesSent  += bytesSent
                    bytesSent       = 0

            # Calculate wait time and sleep so that frames are sent at requested intervals            
            frameEndTime = time.time()
            waitTime = (frameStartTime + self.interval) - frameEndTime
            if waitTime > 0:
                time.sleep(waitTime)
       
            
            ######## Transmit Reset Frame ########

            bytesRemaining = len(self.resetStream) 
            
            streamPosn      = 0
            subframeCounter = 0
            packetCounter   = 0
            bytesSent       = 0
            subframeTotal   = 0       # How much of current subframe has been sent

            frameStartTime = time.time()

            while bytesRemaining > 0:
                
                # Calculate packet size and construct header

                if bytesRemaining <= self.payloadLen:
                    bytesToSend = bytesRemaining
                    header['PacketNumber'] = packetCounter | endOfFrame

                else:
                    
                    subframeRemainder = self.subframeSize - subframeTotal
                    # Would sending full payload contain data from next subframe?
                    if (subframeRemainder < self.payloadLen):
                        bytesToSend = subframeRemainder
                    else:
                        bytesToSend = self.payloadLen
                    header['PacketNumber'] = packetCounter | startOfFrame if packetCounter == 0 else packetCounter
                
                header['SubframeNumber'] = subframeCounter
                header['FrameNumber']    = frame
                    
                # Prepend header to current packet
                packet = header.tostring() + self.resetStream[streamPosn:streamPosn+bytesToSend]

                # Transmit packet
                bytesSent += sock.sendto(packet, (self.host, self.port))

                bytesRemaining  -= bytesToSend
                streamPosn      += bytesToSend
                packetCounter   += 1
                subframeTotal   += bytesToSend

                if subframeTotal >= self.subframeSize:
                    print "  Sent Reset frame:", frame, "subframe:", subframeCounter, "packets:", packetCounter, "bytes:", bytesSent
                    subframeTotal   = 0
                    subframeCounter += 1
                    packetCounter   = 0
                    totalBytesSent  += bytesSent
                    bytesSent       = 0
            
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
