''' Master branch merged
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
    HeaderType = np.dtype([('PacketType', np.uint8), ('SubframeNumber', np.uint8), ('FrameNumber', np.uint32), 
                           ('PacketNumber', np.uint16), ('Information', np.uint8, 14) ])

    ModuleTypeSuperModule = 0
    ModuleTypeTwoTile     = 1
    
    PatternTypePerSection = 0
    PatternTypePerPixel   = 1
    
    def __init__(self, host, port, frames, images, #module, 
                 pattern, interval, display):
        
        self.host = host
        self.port = port
        self.frames = frames
        self.images = images
#        self.module = module
        self.pattern = pattern
        self.interval = interval
        self.display = display
        
        # Initialise shape of data arrays in terms of sections and pixels
        # 1 section = 704 x 742 pixels (columns x rows)
        self.numSectionRows = 2    # 8
        self.numSectionCols = 2    # 16
        self.numPixelRowsPerSection = 742  # 32
        self.numPixelColsPerSection = 704  # 16
        self.numPixelRows = self.numSectionRows * self.numPixelRowsPerSection
        self.numPixelCols = self.numSectionCols * self.numPixelColsPerSection
        self.numPixels    = self.numPixelRows   * self.numPixelCols
        self.numSections  = self.numSectionRows * self.numSectionCols

        # Initialise an array representing a single image in the system
        self.imageArray = np.empty((self.numPixelRows, self.numPixelCols), dtype=np.uint16)
                
        # Fill in image array with the appropriate values depending on the pattern type
        if self.pattern == PercivalUdpProducer.PatternTypePerSection:
            
            # Create pattern with constant value per section, offset is to use full 15-bit range (?)
            # over all 4 sections
            asicVal = 0
            asicValOffset = 8192
            for aRow in range(self.numSectionRows):
                for aCol in range(self.numSectionCols):
                    pixelRowStart = aRow * self.numPixelRowsPerSection
                    pixelRowEnd   = pixelRowStart + self.numPixelRowsPerSection
                    pixelColStart = aCol * self.numPixelColsPerSection
                    pixelColEnd   = pixelColStart + self.numPixelColsPerSection
                    self.imageArray[pixelRowStart:pixelRowEnd, pixelColStart:pixelColEnd] = asicVal
                    asicVal += asicValOffset

        elif self.pattern == PercivalUdpProducer.PatternTypePerPixel:
            
            # Create pattern with constant value per pixel, offset is to use full 15-bit range (well, not really.. 
            #        Can't fit 32k values into 500k pixels without repetition)
            # over all pixels
            pixelVal = 0
            pixelValOffset = 20
            pixelNextVal = 1
            for pRow in range(self.numPixelRowsPerSection):
                for pCol in range(self.numPixelColsPerSection):
                    self.imageArray[pRow::self.numPixelRowsPerSection, pCol::self.numPixelColsPerSection] = pixelVal
                    pixelVal += pixelValOffset
                    # "Reset" pixel value/increment when 15-bit range exceeded
                    if pixelVal >= 2**15:
                        pixelVal = pixelNextVal
                        pixelNextVal += 1 

        else:
            raise PercivalUdpProducerError("Illegal pattern type %d specified" % self.pattern)
            
    
#        # Transform the image array to LPD data stream order
#        pixelStream = np.empty(self.numPixels * self.images, dtype=np.uint16)
#        streamOffset = 0
#        for row in range(self.numPixelRowsPerSection):
#            for col in range(self.numPixelColsPerSection):
#                pixelStream[streamOffset:(streamOffset + self.numSections)] = \
#                    self.imageArray[row::self.numPixelRowsPerSection, col::self.numPixelColsPerSection].reshape(self.numSections)
#                streamOffset += self.numSections
#        
#        # Copy transformed data stream to repeat for number of images per train
#        for image in range(1,self.images):
#            streamOffset = image * self.numPixels
#            pixelStream[streamOffset:(streamOffset+self.numPixels)] = pixelStream[0:self.numPixels] 

        # Convert data stream to byte stream for transmission
        self.byteStream = self.imageArray.tostring()
#        self.byteStream = pixelStream.tostring()


        
        
    def run(self):
        
        self.payloadLen = 8192
        startOfFrame    = 0x80000000
        endOfFrame      = 0x40000000
        self.sectionsPerSubframe = 2
        self.bytesPerPixels      = 2
        self.subframeSize = self.numPixelColsPerSection * self.numPixelRowsPerSection * self.sectionsPerSubframe * self.bytesPerPixels 

        print "Starting Percival data transmission to address", self.host, "port", self.port, "..."
                
        # Open UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Create packet header
        header = np.zeros(22, dtype=np.uint8)
        
        # Load header with dummy values
        header[0] = 85   # Packet Type        (1 Byte)
        header[1] = 171   # Subframe Number    (1 Byte)
        header[2] = 0xA000000A   # Frame Number       (4 Bytes)
        header[6] = 0   # Packet Number      (2 Bytes)
        header[8] = 0   # Information        (14 Bytes)
        
        totalBytesSent = 0
        runStartTime = time.time()
        
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
                    header[6] = packetCounter | endOfFrame
                else:
                    # Will current payload span 2 subframes?
                    subframeRemainder = self.subframeSize - subframeTotal

                    if (subframeRemainder < self.payloadLen):
                        bytesToSend = subframeRemainder
                    else:
                        bytesToSend = self.payloadLen
                    header[6] = packetCounter | startOfFrame if packetCounter == 0 else packetCounter
                
                header[1] = subframeCounter
                header[2] = frame
                subframeTotal += bytesToSend
                if subframeTotal >= self.subframeSize:
                    subframeTotal = 0
                    subframeCounter += 1
                
                # Append header to current packet
                packet = header.tostring() + self.byteStream[streamPosn:streamPosn+bytesToSend]
                
                # Transmit packet
                bytesSent += sock.sendto(packet, (self.host, self.port))

                bytesRemaining -= bytesToSend
                packetCounter += 1
                streamPosn += bytesToSend
                 
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
    parser.add_argument('--images', '-i', type=int, default=1,
                        help='select number of images per frame to transmit')
#    parser.add_argument('--module', '-m', type=int, default=0, choices=[0, 1],
#                        help='select module type (0=supermodule, 1=two-tile)')
    parser.add_argument('--pattern', '-p', type=int, default=0, choices=[0, 1],
                        help='select image pattern (0=per ASIC, 1=per pixel)')
    parser.add_argument('--interval', '-t', type=float, default=0.1,
                        help="select frame interval in seconds")
    parser.add_argument('--display', "-d", action='store_true',
                        help="Enable diagnostic display of generated image")
    
    args = parser.parse_args()

    producer = PercivalUdpProducer(**vars(args))
    producer.run()
    # PercivalDummy
