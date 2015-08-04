'''
Created on July 27, 2015

@author: ckd27546
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
    IP_0_ADDR   = 0x60000000 
    IP_1_ADDR   = 0x70000000
    IP_2_ADDR   = 0x60000004

    # Redundant: ? Not yet at least
    (address0Enabled, address1Enabled, address2Enabled) = (False, False, False)
    (ip_address_0, ip_address_1, ip_address_2) = ("", "", "")

    def __init__(self, host, port, timeout):

        self.host     = host #'192.168.0.111'
        self.port     = port # 4321
        self.timeout  = timeout
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        # Open TCP connection
        try:
            self.sock.connect((host, port))
        except socket.timeout:
            raise FirmwareTestingError("Connecting to [%s:%d] timed out" % (host, port))
            
        except socket.error, e:
            if self.sock:
                self.sock.close()
            raise FirmwareTestingError("Error connecting to [%s:%d]: '%s'" % (host, port, e))

    # Test this stuff:

    def execute(self, command):

        self.command = command
        
        # Debugging Start
        if 1:   #command is FirmwareTesting.LegalCommands['stop']:

#             # Define Mac in IP address for Mezzanine & PC sides
#             macList = []
#             src0mac = "00 : 07 : 11 : F0 : FF : 33"    # Src0 (Mezzanine)
#             dst0mac = "00 : 07 : 43 : 10 : 63 : 00"    # Dst0 (PC)
#             src1mac = "00 : 07 : 11 : F0 : FF : 44"    # Src1 (Mezzanine)
#             dst1mac = "00 : 07 : 43 : 10 : 5F : 20"    # Dst1 (PC)
#             src2mac = "00 : 07 : 11 : F0 : FF : 55"    # Src2 (Mezzanine)
#             dst2mac = "EC : F4 : BB : CC : D3 : A8"    # Dst2 (PC)
#             
#             macList = self.create_mac(src0mac)
#             macSourceStr = ''.join(macList)
#             print "\n-------\nSource0 MAC address converted and should I send? =", macSourceStr, type(macSourceStr)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macSourceStr )
#             time.sleep(1)
            
            src0ip  = "10.1.0.101"    # Src0 (Mezzanine)
            dst0ip  = "10.1.0.1"      # Dst0 (PC)
            src1ip  = "10.1.0.102"    # Src1 (Mezzanine)
            dst1ip  = "10.1.0.2"      # Dst1 (PC)
            src2ip  = "10.1.0.103"    # Src2 (Mezzanine)
            dst2ip  = "10.1.0.3"      # Dst2 (PC)
            
            src0ip  = "10.255.0.1"
            FirmwareTesting.address0Enabled = True
            ipList = self.create_ip(src0ip)
            ipSourceString = ''.join(ipList)
            print "Joined ip string:", ipSourceString
#             print "\n-------\nsource0 IP address converted and should I send? =", ipSourceString, type(ipSourceString)
            self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipSourceString)
            time.sleep(0.1)
            
            
#             # FOR  FUTURE REFERENCE:

#             # Config Mac addresses for PC & Mezzanine
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macList[0 + OFFSET])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_1_ADDR, 6, macList[1])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macList[2])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_1_ADDR, 6, macList[3])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macList[4])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_1_ADDR, 6, macList[5])
#             time.sleep(0.1)
# 
#             # Config IP addresses for PC & Mezzanine IP
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[0])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[1])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[2])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[3])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[4])
#             time.sleep(0.1)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipList[5])
#             time.sleep(0.1)
# 
#         else:
#             
#             print "Business as usual"
#         return
        
        # Debugging finished


# --- New Stuff --- #


    # Python code for converting Mac address and sending (Mac or IP) address to hardware
        
        
    def tokeniser(self, string):
        """ Remove white spaces and Split (IP address) string into list """
        string = string.replace(' ', '')
        if ":" in string:
            tokenList = string.split(":")
        else:
            if "." in string:
                tokenList = string.split(".")
            else:
                tokenList = string.split()
        return tokenList
        
    def create_ip(self, ip_addr):
        ''' Convert IP address from string format into list '''

        ip_value  = ['0'] * 8        # Return value
        int_value = ['0'] * 8
        var_b = ""
        #
        hexString = ""
        var_i = 0
        tokenList = self.tokeniser(ip_addr)
        for index in range(len(tokenList)):
            var_i = 0
            #
            var_i = int(tokenList[index])
            var_b = (var_i & 0x000000FF)
            #
            #hexString = hexString + " %.2X" % (var_i)    # Construct hexadecimal string of IP address
            hexString = hexString + str(tokenList[index] )
            int_value[index] = var_i
            ip_value[index] = '%02X' % (var_b)
            #ip_value[index] = str(var_b)

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
        print "create_ip() (rc'd) ip_addr: ", ip_addr, type(ip_addr), "(ret) ip_value:", ip_value, type(ip_value)
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
    
    def intToByte(self, header, offset, length, offset2, command_b):
        ''' Functionality change so that header inserted into command_b according to offset and offset2 '''
#         print "intToByte() BEFORE command_b '%s', length: %d" % (command_b, length)
        lengthBefore = len(command_b)
        for i in range(length):
            #print "* i: %d header[i]: 0x%08X str(header[i]): %10s.  1st: %2s hdr: '%10s' 2nd: '%s'" % (i, header[i], str(header[i]), command_b[8:(offset2+i)], str(header[i]), command_b[(offset2+i):])
            command_b = command_b[0:(offset2+i)] + str(header[i]) + command_b[(offset2+i):]
#         print "intToByte() AFTER  command_b '%s'" % (command_b)
        return command_b[:lengthBefore]
    
    def send_to_hw(self, Dev_RW, ADDR, Length, data):
        ''' Send (IP/Mac address) to Mezzanine '''
        # Example :
        # Device ID  = 0x40000001;  # HW,  Write
        # Address  = 0x0x18000004;  # Control Register   
        # length  = 0x0x00000001;   # Control Register   
        HEADER = [0,0,0,0]
        HEADER[0] = Dev_RW; HEADER[1] = ADDR;  HEADER[2] = Length;
        # Extract "start" key from dictionary, store locally as string
        command = FirmwareTesting.LegalCommands[self.command] + "                    " # Add 20 empty spaces in string allowing for formatted Mac/IP address to fit 
        #
        
#         print "send_to_hw() BEFORE command '%s'" % (command)
        command = self.intToByte( HEADER, 0, 3, 8, command)
#         print "send_to_hw() AFTER  command '%s'" % (command)
        
#         print "send_to_hw() early exit"
#         return
        print "DEBUG command length %d" % len(command)
        print "DEBUG command before (/wo sp-chars): '%s%s'" % (command[:6], command[8:])
        try:
            for i in range(Length*2):
#                 print " ** ", i, " begin: '%s' data[i]: '%s' end: '%s'" % (command[8:(20+i)], data[i], command[(20+i):] )
                command = command[:(20+i)] +  str(data[i]) + command[(20+i):]
                #command[20+i] = data[i]
        except Exception as e:
            print " ** Exception at Index: %d out of %d. Error: %s" % (i, Length, e)
        print "send_to_hw() command: '%s' " % command
#         return command
        print "DEBUG command length %d" % len(command)
        
        # Transmit command
        try:
            bytesSent = self.sock.send(command)
        except socket.error, e:
            if self.sock:
                self.sock.close()
            raise EmulatorClientError("Error sending %s command: %s" % (command, e))
        
        print " * Sent %d bytes." % (bytesSent)
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="FirmwareTesting - control hardware emulator start/stop")
    
    parser.add_argument('--host', type=str, default='192.168.0.111', 
                        help="select emulator IP address")
    parser.add_argument('--port', type=int, default=4321,
                        help='select emulator IP port')
    parser.add_argument('--timeout', type=int, default=5,
                        help='set TCP connection timeout')
    parser.add_argument('command', choices=FirmwareTesting.LegalCommands.keys(), default="start",
                        help="specify which command to send to emulator")

    args = parser.parse_args()
    try:
        client = FirmwareTesting(args.host, args.port, args.timeout)
        client.execute(args.command)
    except Exception as e:
        print e
        
