'''
    LpdReadoutTest.py - Readout a system using the API
                    
'''

from LpdDevice.LpdDevice import LpdDevice
from EthernetUtility import EthernetUtility 
import argparse, sys
from datetime import datetime

# New imports
from xml.etree.ElementInclude import ElementTree
from xml.etree.ElementTree import ParseError

# Debugging area #

## New stuff
Eth_Dev_RW   = 0x00000001

MAC_0_ADDR   = 0x80000006 
MAC_1_ADDR   = 0x80000000 
MAC_2_ADDR   = 0x80000012
IP_0_ADDR   = 0x60000000 
IP_1_ADDR   = 0x70000000
IP_2_ADDR   = 0x60000004

#     private void MAC_ADDR_2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_MAC_ADDR_2ActionPerformed
#         String mac_add = MAC_ADDR_2.getText();
#        send_to_hw(Eth_Dev_RW, MAC_2_ADDR, 6, create_mac(mac_add));
#     }//GEN-LAST:event_MAC_ADDR_2ActionPerformed

def intToByte(header, offset, length, offset2, command_b):
    ''' Functionality change so that header inserted into command_b according to offset and offset2 '''
    for i in range(length):
        command_b = command_b[0:(offset2+i)] + str(header[i]) + command_b[(offset2+i):]
        
#         command_b[offset2+i*4]   = (header[i+offset] & 0xff000000) >> 24 
#         command_b[offset2+i*4+1] = (header[i+offset] & 0x00ff0000) >> 16
#         command_b[offset2+i*4+2] = (header[i+offset] & 0x0000ff00) >> 8
#         command_b[offset2+i*4+3] =  header[i+offset] & 0x000000ff

# ---- Original Java code: intToByte() ---- #
public void intToByte(int[] Iarr, int offset, int length, int offset2,  byte LocArr[]) { 
    for(int i=0; i<length; i++) { 
        LocArr[offset2+i*4]   = (byte)((Iarr[i+offset] & 0xff000000) >>> 24);   #  var1 >>> var2. Shift right unsigned - Shift x to the right by y bits. Low order bits lost. Zeros fill in left bits regardless of sign. 
        LocArr[offset2+i*4+1] = (byte)((Iarr[i+offset] & 0x00ff0000) >>> 16);
        LocArr[offset2+i*4+2] = (byte)((Iarr[i+offset] & 0x0000ff00) >>> 8);
        LocArr[offset2+i*4+3] = (byte)( Iarr[i+offset] & 0x000000ff);
    }
} 
# create_mac() returns:     mac_value = [0] * 8
# Define legal commands
LegalCommands = {
             "start" : "startd\n\r",
             "stop"  : "stopd\n\r\r"
             }

def send_to_hw(Dev_RW, ADDR, Length, data):
    ''' Send (IP/Mac address) to Mezzanine '''
    HEADER = [0,0,0,0]
    HEADER[0] = Dev_RW; HEADER[1] = ADDR;  HEADER[2] = Length;
    # Extract "start" key from dictionary, store locally as string
    command_b = LegalCommands['start'] + "                    " # Add 20 empty spaces in string allowing for formatted Mac/IP address to fit 
    #
    intToByte( HEADER, 0, 3, 8, command_b)
    #
    for i in range(Length):
        command_b = command_b[:(20+i)] + data[i] + command_b[(20+i):]
        #command_b[20+i] = data[i]
    # Example :
    # Device ID  = 0x40000001;  # HW,  Write
    # Address  = 0x0x18000004;  # Control Register   
    # length  = 0x0x00000001;   # Control Register   
    return command_b
    #TODO: Transmit command_b

# ---- Original Java code: send_to_ hw() ---- #
private void send_to_hw(int Dev_RW, int ADDR, int Length, byte[] data) { 
  
    int HEADER[] = {0,0,0,0};
    HEADER[0] = Dev_RW; HEADER[1] = ADDR;  HEADER[2] = Length;
    NumConv.intToByte( HEADER, 0, 3, 8, command_b);
    for(int i=0; i<Length; i++) {
        command_b[20+i] = data[i];
    }
    // Example :
    // Device ID  = 0x40000001;  // HW,  Write
    // Address  = 0x0x18000004;  // Control Register   
    // length  = 0x0x00000001;   // Control Register   
    
    try{
      DataOutputStream  cmd_out  =  (DataOutputStream)TCPcln1.Datout;
      cmd_out.write(command_b, 0, Length+20);
    } catch ( Exception e3 ) {
      System.err.println( "Try to close connection port:  4321  "  + e3 );
    }
}
# ---- Original Java code ---- #

# Config PC MAC
send_to_hw(Eth_Dev_RW, MAC_0_ADDR, 6, create_mac(mac_addr0P))
send_to_hw(Eth_Dev_RW, MAC_0_ADDR, 6, create_mac(mac_addr1M))
    

def tokeniser(string):
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

# Convert create_mac() into Python
def create_mac(mac_add):
    mac_value = [0] * 8
    int_value = [0] * 8
    var_b   = [0]    #TODO: byte type, in Python should be..?
    lenToken = 0
    var_i = 0
    hdata = ""   #TODO: Receives char at specified index; string appropriate choice?
    hexString = ""
    tokenList = tokeniser(mac_add)
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
    #
    print "MAC Addr Hex =  ", hexString
    print "MAC Addr Int   %d:%d:%d%d:%d:%d" % (int_value[0], int_value[1], int_value[2], int_value[3], int_value[4], int_value[5])
    return mac_value 

# Change MAC address
mac_addr0P = "00 : 07 : 11 : F0 : FF : 33"    # Src0 (PC end)
mac_addr1M = "00 : 07 : 43 : 10 : 63 : 00"    # Dst0 (Mezzanine)
# Test create_mac() function:
address0PC = create_mac(mac_addr0P)
address1M = create_mac(mac_addr1M)


# --- Original Java code --- #

  private byte[] create_mac(String mac_add) {      

        byte mac_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
        int int_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
        byte var_b, lenb;
        String prtstring = "";
        int i = 0;
        int add = 0, len;
        int var_i = 0;
        char hdata[] ={'0'};
        
        StringTokenizer tok = new StringTokenizer(mac_add,":. \t\n\r\f");
        while (tok.hasMoreTokens()) {
            String  cur_del = tok.nextToken();
            var_i = 0;
            len = cur_del.length();
            lenb = (byte)len;
            
            for(byte k = 0; k<len; k++){
                hdata[0] = cur_del.charAt(k);                   # charAt(index) returns character at index position
                String hex_16 = new String(hdata);
                var_b = Byte.valueOf(hex_16,16).byteValue();    # Byte.valueOf(str, int) returns byte holding value within str parsed by radix int;
                                                                # .byteValue()  returns numeric value represented by this object after conversion to type byte.
                var_i = var_i + var_b*((len-1-k)*16 + k) ;
            }
            prtstring = prtstring + cur_del;
            int_value[i] = var_i;
            mac_value[i] = (byte)var_i;
            //add = add + i_delay;
            i++;
        }
         System.out.println("MAC Addr Hex =  "  + prtstring); 
         System.out.println("MAC Addr Int  "  + int_value[0] + ":" + int_value[1] + ":" + int_value[2] + ":"
                  + int_value[3] + ":" + int_value[4] + ":" + int_value[5]);  
  return mac_value;
} 

#### Original Java code for create_ip()         ####



# Java original code:

private byte[] create_ip(String ip_addr) {                                            

    byte ip_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
    int int_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
    byte var_b, lenb;	# lenb is redundant
    String prtstring = "";
    int i = 0;
    int add = 0, len;	# add is redundant
    int var_i = 0;
    #..
    #            char hdata[] ={'0'};
    #           //String del_values = Control_Reg.getText();
    #
    StringTokenizer tok = new StringTokenizer(ip_addr,":. \t\n\r\f");
    while (tok.hasMoreTokens()) {
        String  cur_del = tok.nextToken();
        var_i = 0;
        len = cur_del.length();
        lenb = (byte)len;       	# lenb is redundant

        var_i = Integer.valueOf(cur_del).intValue();
        var_b = (byte)(var_i & 0x000000FF);

        prtstring = prtstring + cur_del;
        int_value[i] = var_i;
        ip_value[i] = var_b;
        //add = add + i_delay;
        i++;
    }
    System.out.println("IP Addr Hex =  "  + prtstring); 
    String temp_addr = "" +  int_value[0] + "." + int_value[1] + "." + int_value[2] + "." + int_value[3]; 
    if (addr_0){ ip_address_0 = temp_addr; addr_0 = false; }
    if (addr_1){ ip_address_1 = temp_addr; addr_1 = false; }
    if (addr_2){ ip_address_2 = temp_addr; addr_2 = false;}
    System.out.println("IP Addr Clean : "  + temp_addr + "  "+ip_address_0+ "  "+ip_address_1+ "  "+ip_address_2);

    return ip_value; 
} 

# ---------------------------------------------------------------------- #

# Java code with the redundant bits removed:

private byte[] create_ip(String ip_addr) {                                            

    byte ip_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
    int int_value[] = {0, 0, 0, 0, 0, 0, 0, 0};
    byte var_b;
    String prtstring = "";
    int i = 0;
    int len;
    int var_i = 0;
    StringTokenizer tok = new StringTokenizer(ip_addr,":. \t\n\r\f");
    while (tok.hasMoreTokens()) {
        String  cur_del = tok.nextToken();
        var_i = 0;
        len = cur_del.length();

        var_i = Integer.valueOf(cur_del).intValue();
        var_b = (byte)(var_i & 0x000000FF);

        prtstring = prtstring + cur_del;
        int_value[i] = var_i;
        ip_value[i] = var_b;
        i++;
    }

    return ip_value; 
} 



####  Kept this below in case it might prove useful in the future #####

if __name__ == '__main__':

    # Default values
    femHost = '192.168.2.2'
    femPort = 6969  # oneGig port
    tenGig  = 2     # eth2 on devgpu02
    destIp  = None  # Default: Assume tenGig destination IP is one increment above eth2's IP
    
    # Create parser object and arguments
    parser = argparse.ArgumentParser(description="LpdReadoutTest.py - configure and readout an LPD detector. ",
                                     epilog="Defaults: tengig=(eth)2, destip=10.0.0.2, femhost=192.168.2.2, femport=6969")

    parser.add_argument("--tengig",     help="Set tenGig ethernet card (e.g. 2 for eth2)",  type=int, default=tenGig)
    parser.add_argument("--destip",     help="Set destination IP (eg 10.0.0.2)",            type=str, default=destIp)
    parser.add_argument("--femhost",    help="Set fem host IP (e.g.  192.168.2.2)",         type=str, default=femHost)
    parser.add_argument("--femport",    help="Set fem port (eg 61649)",                     type=int, default=femPort)
    args = parser.parse_args()

    # Copy value(s) for the provided arguments
    if args.tengig != None:
        tenGig = args.tengig

    if args.femhost:
        femHost = args.femhost

    if args.femport:
        femPort = args.femport

    if args.destip:
        destIp = args.destip

    LpdReadoutTest(tenGig, femHost, femPort, destIp)
