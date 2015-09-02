'''
Created on July 27, 2015

@author: ckd27546

    Acting as TCP client
'''

import argparse, socket, time

class FirmwareTestingError(Exception):
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return repr(self.msg)


class FirmwareTesting(object):
    ''' Test setting IP/MAC addresses in the firmware '''
 
    # Define legal commands #TODO: To include MAC/IP address?
    LegalCommands = {
                     "start"   : "startd\n\r",
                     "command" : "COMAND\n\r",
                     "stop"    : "stopd\n\r\r"
                     }

    ## New stuff
    Eth_Dev_RW   = 0x00000001
    
    MAC_0_ADDR   = 0x80000006 
    MAC_1_ADDR   = 0x80000000 
    MAC_2_ADDR   = 0x80000012
    MAC_3_ADDR   = 0x8000000C 
    MAC_4_ADDR   = 0x8000001E                                       
    MAC_5_ADDR   = 0x80000018                                       
    MAC_6_ADDR   = 0x8000002A                                       
    MAC_7_ADDR   = 0x80000024 
    MAC_8_ADDR   = 0x80000036                                       
    MAC_9_ADDR   = 0x80000030                                       
    MAC_10_ADDR  = 0x80000042
    MAC_11_ADDR  = 0x8000003C
    MAC_12_ADDR  = 0x8000004E                                       
    MAC_13_ADDR  = 0x80000048                                       
    MAC_14_ADDR  = 0x8000005A                                       
    MAC_15_ADDR  = 0x80000054 

    IP_0_ADDR    = 0x60000000 
    IP_1_ADDR    = 0x70000000
    IP_2_ADDR    = 0x60000004
    IP_3_ADDR    = 0x70000004                                       
    IP_4_ADDR    = 0x60000008       
    IP_5_ADDR    = 0x70000008                                       
    IP_6_ADDR    = 0x6000000C                                       
    IP_7_ADDR    = 0x7000000C                                       
    IP_8_ADDR    = 0x60000010       
    IP_9_ADDR    = 0x70000010                                       
    IP_10_ADDR   = 0x60000014                                       
    IP_11_ADDR   = 0x70000014                                       
    IP_12_ADDR   = 0x60000018       
    IP_13_ADDR   = 0x70000018                                       
    IP_14_ADDR   = 0x6000001C                                       
    IP_15_ADDR   = 0x7000001C   
      
    (IP, MAC)    = (0, 1)
    # Redundant: ? Not yet at least
    (address0Enabled, address1Enabled, address2Enabled) = (False, False, False)
    (ip_address_0, ip_address_1, ip_address_2) = ("", "", "")

    def __init__(self, host, port, timeout, src0addr, src1addr, src2addr, dst0addr, dst1addr, dst2addr):

        self.host     = host #'192.168.0.111'
        self.port     = port # 4321
        self.timeout  = timeout
        
        if src0addr: self.src0addr = self.extractAddresses(src0addr) 
        else:        self.src0addr = (None, None)
        if src1addr: self.src1addr = self.extractAddresses(src1addr) 
        else:        self.src1addr = (None, None)
        if src2addr: self.src2addr = self.extractAddresses(src2addr) 
        else:        self.src2addr = (None, None)
        if dst0addr: self.dst0addr = self.extractAddresses(dst0addr) 
        else:        self.dst0addr = (None, None)
        if dst1addr: self.dst1addr = self.extractAddresses(dst1addr) 
        else:        self.dst1addr = (None, None)
        if dst2addr: self.dst2addr = self.extractAddresses(dst2addr) 
        else:        self.dst2addr = (None, None)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        # Open TCP connection
        try:
            self.sock.connect((host, port))
        except socket.timeout:
            raise FirmwareTestingError("FW Connecting to [%s:%d] timed out" % (host, port))
            
        except socket.error, e:
            if self.sock:
                self.sock.close()
            raise FirmwareTestingError("FW Error connecting to [%s:%d]: '%s'" % (host, port, e))

    def extractAddresses(self, jointAddress):
        ''' Extracting mac/IP from parser argument '''
        delim =  jointAddress.find(":")
        ip    = jointAddress[:delim]
        mac   = jointAddress[delim+1:]
        return (ip, mac)

    def execute(self, command):

        self.command = command
        
        if not command in FirmwareTesting.LegalCommands:
            raise FirmwareTestingError("Illegal command %s specified" % command)
        
        if (command == 'start') or (command == 'stop'):

            # Transmit command
            try:
                bytesSent = self.sock.send(FirmwareTesting.LegalCommands[command])
            except socket.error, e:
                if self.sock:
                    self.sock.close()
                raise FirmwareTestingError("Error sending %s command: %s" % (command, e))
                
            if bytesSent != len(FirmwareTesting.LegalCommands[command]):
                print "Failed to transmit %s command properly" % command
            else:
                print "Transmitted %s command" % command
        else:
            
            # Configure link(s) 

            theDelay = 2.480  # Between each TCP transmission
            
#             debugList = [self.src0addr, self.src1addr, self.src2addr, self.dst0addr, self.dst1addr, self.dst2addr]
#             print "MAC addresses.."
#             for index in range(len(debugList)): print " Before:\t", debugList[index]
            src0mac = self.src0addr[FirmwareTesting.MAC]
            src1mac = self.src1addr[FirmwareTesting.MAC]
            src2mac = self.src2addr[FirmwareTesting.MAC]
            dst0mac = self.dst0addr[FirmwareTesting.MAC]
            dst1mac = self.dst1addr[FirmwareTesting.MAC]
            dst2mac = self.dst2addr[FirmwareTesting.MAC]
#             debugList = [src0mac, src1mac, src2mac, dst0mac, dst1mac, dst2mac]
#             for index in range(len(debugList)): print " After: \t", debugList[index]
            
            if src0mac:
                tokenList = self.tokeniser(src0mac)
                macSourceStr = ''.join(tokenList)
                #print "src0mac -> tokenList: '%s' macSourceStr: '%s'"  % (tokenList, macSourceStr)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macSourceStr)
                time.sleep(theDelay)
#
            if dst0mac:
                tokenList = self.tokeniser(dst0mac)
                macSourceStr = ''.join(tokenList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_1_ADDR, 6, macSourceStr)
                time.sleep(theDelay)
     
            if src1mac:
                tokenList = self.tokeniser(src1mac)
                macSourceStr = ''.join(tokenList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_2_ADDR, 6, macSourceStr)
                time.sleep(theDelay)
#
            if dst1mac:
                tokenList = self.tokeniser(dst1mac)
                macSourceStr = ''.join(tokenList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_3_ADDR, 6, macSourceStr)
                time.sleep(theDelay)
     
            if src2mac:
                tokenList = self.tokeniser(src2mac)
                macSourceStr = ''.join(tokenList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_4_ADDR, 6, macSourceStr)
                time.sleep(theDelay)
#
            if dst2mac:
                tokenList = self.tokeniser(dst2mac)
                macSourceStr = ''.join(tokenList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_5_ADDR, 6, macSourceStr)
                time.sleep(theDelay)

            src0ip = self.src0addr[FirmwareTesting.IP]
            src1ip = self.src1addr[FirmwareTesting.IP]
            src2ip = self.src2addr[FirmwareTesting.IP]
            dst0ip = self.dst0addr[FirmwareTesting.IP]
            dst1ip = self.dst1addr[FirmwareTesting.IP]
            dst2ip = self.dst2addr[FirmwareTesting.IP]
#             print "IP addresses.."
#             debugList = [src0ip, src1ip, src2ip, dst0ip, dst1ip, dst2ip]
#             for index in range(len(debugList)): print " After: \t", debugList[index]

            if src0ip:
                FirmwareTesting.address0Enabled = True
                ipList = self.create_ip(src0ip)
                ipSourceString = ''.join(ipList)
#                 print "src0ip -> ipList:", ipList, " ipSourceString: ", ipSourceString
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipSourceString)
                time.sleep(theDelay)
#
            if dst0ip:
                ipList = self.create_ip(dst0ip)
                ipSourceString = ''.join(ipList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_1_ADDR, 4, ipSourceString)
                time.sleep(theDelay)
                 
            if src1ip:
                FirmwareTesting.address1Enabled = True
                ipList = self.create_ip(src1ip)
                ipSourceString = ''.join(ipList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_2_ADDR, 4, ipSourceString)
                time.sleep(theDelay)
#
            if dst1ip:
                ipList = self.create_ip(dst1ip)
                ipSourceString = ''.join(ipList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_3_ADDR, 4, ipSourceString)
                time.sleep(theDelay)
                 
            if src2ip:
                FirmwareTesting.address2Enabled = True
                ipList = self.create_ip(src2ip)
                ipSourceString = ''.join(ipList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_4_ADDR, 4, ipSourceString)
                time.sleep(theDelay)
#
            if dst2ip:
                ipList = self.create_ip(dst2ip)
                ipSourceString = ''.join(ipList)
                self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_5_ADDR, 4, ipSourceString)
                time.sleep(theDelay)


    def tokeniser(self, string):
        """ Remove white spaces and Split (IP/MAC address) string into list """
        string = string.replace(' ', '')
        if ":" in string:
            tokenList = string.split(":")
        else:
            if "." in string:
                tokenList = string.split(".")
            else:
                if "-" in string:
                    tokenList = string.split("-")
                else:
                    tokenList = string.split()
        return tokenList
        
    def create_ip(self, ip_addr):
        ''' Convert IP address from string format into list '''

        ip_value  = ['0'] * 4        # Return value
        int_value = ['0'] * 4
        var_b = ""

        hexString = ""
        var_i = 0
        tokenList = self.tokeniser(ip_addr)
        for index in range(len(tokenList)):
            var_i = 0

            var_i = int(tokenList[index])
            var_b = (var_i & 0x000000FF)

            hexString = hexString + str(tokenList[index] )
            int_value[index] = var_i
            ip_value[index] = '%02X' % (var_b)  # Hexadecimal conversion

        #TODO: Redundant section: (Only translated from Java source code)
        #print "IP Addr Hex =  ", hexString
        temp_addr = "" + str(int_value[0]) + "." + str(int_value[1]) + "." + str(int_value[2]) + "." + str(int_value[3]) 
        if FirmwareTesting.address0Enabled:
            FirmwareTesting.ip_address_0 = temp_addr
            address0Enabled = False
        if FirmwareTesting.address1Enabled:
            FirmwareTesting.ip_address_1 = temp_addr
            address1Enabled = False
        if FirmwareTesting.address2Enabled:
            FirmwareTesting.ip_address_2 = temp_addr
            address2Enabled = False 
        #print "IP Addr Clean : ", temp_addr, " ip0: ", FirmwareTesting.ip_address_0, " ip1: ", FirmwareTesting.ip_address_1, " ip2: ", FirmwareTesting.ip_address_2
        #print "create_ip() (rc'd) ip_addr: ", ip_addr, type(ip_addr), "(ret) ip_value:", ip_value, type(ip_value)
        
        return ip_value     # Returns IP address as a list of integers 
    
    
    # Convert create_mac() into Python
    def create_mac(self, mac_add):
        mac_value = ['0'] * 8
        int_value = ['0'] * 8
        var_b   = [0]    #TODO: byte type, in Python should be..?
        lenToken = 0
        var_i = 0
        hdata = ""   #TODO: Receives char at specified index; string appropriate choice?
        hexString = ""
        tokenList = self.tokeniser(mac_add)
        for index in range(len(tokenList)):
            cur_del = tokenList[index]  #TODO: rename cur_del to token
            var_i = 0
            #
            var_i = int(tokenList[index], 16)
            lenToken = len(cur_del)
            var_b = (var_i & 0x000000FF)
            #lenb = (byte)len    # lenb: Never Used
            
            for k in range(lenToken):
                hdata = cur_del[k]
                hex_16 = str(hdata)         # Redundant step, hdata already a string
                var_b = int(hex_16, 16) 
                var_i = var_i + var_b*((lenToken-1-k)*16 + k)     #TODO:Is this really right???? 
            
            hexString = hexString + cur_del#hex(cur_del)[2:]    # hex(15) -> '0xf'; hex(15)[2:] -> 'f'
            int_value[index] = var_i
            mac_value[index] = str(var_b)   #TODO: Forced string conversion redundant here?

#         print "MAC Addr Hex =  ", hexString.upper()
#         print "MAC Addr Int   %d:%d:%d:%d:%d:%d" % (int_value[0], int_value[1], int_value[2], int_value[3], int_value[4], int_value[5])
        return mac_value 

    def new_function(self, mac_add):
        tokenList = self.tokeniser(mac_add)
        macString = ""
        for token in tokenList:
            hexPadded  = (token).zfill(2)
            byteString = ''.join(chr(int(hexPadded[i:i+2], 16)) for i in range(0, len(hexPadded), 2))
            macString  = macString + byteString 
        return macString
    
    def intToByte(self, header, offset, length, offset2, command_b):
        ''' Functionality change so that header inserted into command_b according to offset and offset2 '''
        # header is a list of integers, turn them into 8 digits hexadecimals
        for index in range(len(header)):
            hexNum     = "%x" % header[index]
            hexPadded  = (hexNum).zfill(8)
            byteString = ''.join(chr(int(hexPadded[i:i+2], 16)) for i in range(0, len(hexPadded), 2))
            command_b  = command_b[:8+(index*4)] + byteString + command_b[8+((index+1)*4):]
        return command_b
    
    def send_to_hw(self, Dev_RW, ADDR, Length, data):
        ''' Send (IP/Mac address) to Mezzanine '''
        # Example :
        # Device ID  = 0x40000001;  # HW,  Write
        # Address    = 0x18000004;  # Control Register   
        # length     = 0x00000001;  # Control Register    0x0000 0001
        HEADER = [0,0,0,0]
        HEADER[0] = Dev_RW; HEADER[1] = ADDR;  HEADER[2] = Length;
        
        # Extract "start" key from dictionary, store locally as string
        command = FirmwareTesting.LegalCommands[self.command] + "0"* 16 # Add 16 empty spaces for header + data
        #print "OVERRIDING command";command = 'COMAND\n\rABCDEFGHIJKLMNOP'
        #
        before = len(command)
        
        command = self.intToByte( HEADER, 0, 3, 8, command)
        #print "%d char's, command: '%s..%s'" % (len(command), command[:6], command[8:]), " After intToByte() called."
        try:
            results =''.join(chr(int(data[i:i+2], 16)) for i in range(0, len(data), 2))
            command = command[:20] +  results
        except Exception as e:
            print "FW ** Exception: %s" % e
        
        #print "About to transmit '%s..%s', %d character(s).  ['..'=2 special characters]" % (command[:6], command[8:], len(command))
        
        # Transmit command
        try:
            bytesSent = self.sock.send(command)
        except socket.error, e:
            if self.sock:
                self.sock.close()
            raise FirmwareTestingError("FW Error sending %s command: %s" % (command, e))
        else:
            print " * Sent %d bytes." % (bytesSent)
    


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="FirmwareTesting - control hardware emulator start/stop", epilog="Specify IP & Mac like: '10.1.0.101:00-07-11-F0-FF-33'")
    
    parser.add_argument('--host', type=str, default='192.168.0.111', 
                        help="select emulator IP address")
    parser.add_argument('--port', type=int, default=4321,
                        help='select emulator IP port')
    parser.add_argument('--timeout', type=int, default=5,
                        help='set TCP connection timeout')

    parser.add_argument('--src0', type=str, 
                        help='Configure Mezzanine link 0 IP:MAC addresses')
    parser.add_argument('--src1', type=str, 
                        help='Configure Mezzanine link 1 IP:MAC addresses')
    parser.add_argument('--src2', type=str, 
                        help='Configure Mezzanine link 2 IP:MAC addresses')
    
    parser.add_argument('--dst0', type=str, 
                        help='Configure PC link 0 IP:MAC addresses')
    parser.add_argument('--dst1', type=str, 
                        help='Configure PC link 1 IP:MAC addresses')
    parser.add_argument('--dst2', type=str, 
                        help='Configure PC link 2 IP:MAC addresses')
    
    parser.add_argument('command', choices=FirmwareTesting.LegalCommands.keys(), default="start",
                        help="specify which command to send to emulator")

    args = parser.parse_args()
    try:
        client = FirmwareTesting(args.host, args.port, args.timeout, args.src0, args.src1, args.src2, args.dst0, args.dst1, args.dst2)
#         print " *** parser hijacked"
#         print "args: ", args, args.__dict__
#         args.command = "command"
        client.execute(args.command)
    except Exception as e:
        print e
#         
#  --src0 10.1.0.101:00-07-11-F0-FF-33
#  --dst0 10.1.0.1:00-07-43-10-63-00
#  --src1 10.1.0.102:00-07-11-F0-FF-44
#  --dst1 10.1.0.2:00-07-43-10-5F-20
#  --src2 10.1.0.103:00-07-11-F0-FF-55
#  --dst2 10.1.0.3:EC-F4-BB-CC-D3-A8
