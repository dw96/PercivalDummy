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
                     "start" : "startd\n\r",
                     "stop"  : "stopd\n\r\r"
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
    (address0Enabled, address1Enabled, address2Enabled) = (True, True, True)
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

        # Debugging Start
        if 1:   #command is FirmwareTesting.LegalCommands['stop']:

            # Define Mac in IP address for 1st link
            mac_addr0MZ = "11 : 07 : 11 : F0 : FF : 11"    # Src0 (Mezzanine)
            mac_addr1PC = "00 : 07 : 43 : 10 : 63 : 00"    # Dst0 (PC)
            ip_addr0MZ  = "10.1.0.55"   # Src0 (Mezzanine)
            ip_addr1PC  = "10.1.0.3"    # Dst0 (PC)
            
            macAddress0MZ = self.create_mac(mac_addr0MZ)
            macAddress1PC = self.create_mac(mac_addr1PC)
            print ": create_ip()"
            ipAddress0MZ = self.create_ip(ip_addr0MZ)
            ipAddress1PC = self.create_ip(ip_addr1PC)
            
            # Config PC & Mezzanine
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_0_ADDR, 6, macAddress0MZ)
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.MAC_1_ADDR, 6, macAddress1PC)
#             print " Configuring IP address.."
#             # Config PC & MZ IP
#             print "* 1"
#             self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_0_ADDR, 4, ipAddress0MZ)
            print "* 2"
            self.send_to_hw(FirmwareTesting.Eth_Dev_RW, FirmwareTesting.IP_1_ADDR, 6, ipAddress1PC)
            print "* through"
        else:
            
            print "Business as usual"
        return
        
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
#         (address0Enabled, address1Enabled, address2Enabled) = (True, True, True)    # REMOVE THIS LINE
#         (FirmwareTesting.ip_address_0, FirmwareTesting.ip_address_1, FirmwareTesting.ip_address_2) = ("", "", "")            # REMOVE THIS LINE
        #
        ip_value  = [0] * 8        # Return value
        int_value = [0] * 8
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
            hexString = hexString + " %.2X" % (var_i)    # Construct hexadecimal string of IP address
            int_value[index] = var_i
            ip_value[index] = str(var_b)
        #TODO: Uncomment Next-line?
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
        #TODO:  Uncomment previous line?     
        return ip_value     # Returns IP address as a list of integers 
    
    
    # Convert create_mac() into Python
    def create_mac(self, mac_add):
        mac_value = [0] * 8
        int_value = [0] * 8
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
    #        var_i = int(tokenList[index])
            lenToken = len(cur_del)
            var_b = (var_i & 0x000000FF)
            #lenb = (byte)len    # lenb: Never Used
            
            for k in range(lenToken):
                hdata = cur_del[k]
                hex_16 = str(hdata)         # Redundant step, hdata already a string
                var_b = int(hex_16, 16) 
                var_i = var_i + var_b*((lenToken-1-k)*16 + k)     #TODO:Is this really right???? 
            
            hexString = hexString + cur_del
            int_value[index] = var_i
            mac_value[index] = str(var_b)   #TODO: Forced string conversion redundant here?

        #TODO: Uncomment these?
        #print "MAC Addr Hex =  ", hexString
        #print "MAC Addr Int   %d:%d:%d%d:%d:%d" % (int_value[0], int_value[1], int_value[2], int_value[3], int_value[4], int_value[5])
        return mac_value 
    
    
    def intToByte(self, header, offset, length, offset2, command_b):
        ''' Functionality change so that header inserted into command_b according to offset and offset2 '''
        for i in range(length):
            command_b = command_b[0:(offset2+i)] + str(header[i]) + command_b[(offset2+i):]
            
    
    def send_to_hw(self, Dev_RW, ADDR, Length, data):
        ''' Send (IP/Mac address) to Mezzanine '''
        HEADER = [0,0,0,0]
        HEADER[0] = Dev_RW; HEADER[1] = ADDR;  HEADER[2] = Length;
        # Extract "start" key from dictionary, store locally as string
        command_b = FirmwareTesting.LegalCommands['start'] + "                    " # Add 20 empty spaces in string allowing for formatted Mac/IP address to fit 
        #
        self.intToByte( HEADER, 0, 3, 8, command_b)
        #
##        X = 8
##        print "For loop within send_to_HW(), command_b: '%s%s'" % (command_b[:6], command_b[X:])
        try:
            for i in range(Length):
##                print " ** ", i, " Contents, 1st: '%s'" % command_b[X:(20+i)], " 2nd: ", data[i], " 3rd: ", command_b[(20+i):],
##                print "Types, 1st: %s, 2nd: %s 3rd: %s" % (type(command_b[:(20+i)]), type(data[i]), type(command_b[(20+i):]))
                command_b = command_b[:(20+i)] +  str(data[i]) + command_b[(20+i):]
                #command_b[20+i] = data[i]
        except Exception as e:
            print " ** Exception at Index: %d out of %d. Error: %s" % (i, Length, e)
##        print "Finished concatenation"
##        print "command_b: '%s' " % command_b
        # Example :
        # Device ID  = 0x40000001;  # HW,  Write
        # Address  = 0x0x18000004;  # Control Register   
        # length  = 0x0x00000001;   # Control Register   
        return command_b
    
# --- End of Stuff --- #

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
        
