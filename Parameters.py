"""Changes made here will effect the parameters taken for each effect"""

cmd_latency = '-l'
cmd_packetloss = '-pl'
cmd_target_packet = '-tp'
cmd_print = '-p'
cmd_bandwidth = '-b'
cmd_throttle = '-t'
cmd_simulate = '-s'
cmd_ratelimit = '-rl'
cmd_combination = '-c'
cmd_outoforder = '-o'
cmd_arp = '-a'
cmd_save = '-sa'
cmd_graph = '-g'
cmd_edit = '-e'

cmd_flood = '-fs'
cmd_arp_spam = '-as'


def Usage():
    return"""
## ---- Effects:

--print, -p                                  
    * Prints all the packets
    
--ignore, -i
    * Does nothing to the packets. Used to show how much overhead there
    by default
    
--display-bandwidth, -b                     
    * Displays information on the transfer rate
      
--latency, -l <delay_ms>            
    * Applies latency on the connection   
    
--packet-loss, -pl  <loss_percentage>  
    * Performs packet loss on the connection

--surge, -t      <delay_ms> 
    * Creates a packet surge on connection by the given delay 

--simulate, -s      <connection_name>        
    * Simulates real world connections
    
        Supported connections:
        
            - 3G
            - 4G
            - Wifi
            - NoConnection
    
--rate-limit, -rl   <rate_bytes>            
    * Limits the throughput of the program
                                
--combination, -c   <latency_ms> <packet-loss> <bandwidth_bytes>
    * Performs latency and packet loss at the same time
    
--out-of-order, -o 
    * Sets the mode to out of order that alters the order of incoming packets
    
--edit-packets, -e <edit_mode>
    * Sets the mode to mangle packets in certain ways specified by the 'edit_mode'
    
        Edit Modes
        
            1 - TTL Incrementing
              
## ---- Attacks:

--udp-flood, -f   <target_ip> 
    * Attacks a target IP address with a barrage of UDP packets
    
--arp-spam, -as
    * Starts spamming the network with incorrect ARP values
                                
## ---- Extra Optionals:

--target-packet, -tp    <packet-type>        
    * Only performs an affect on the specified packet type

--arp, -a               <victimIP> <routerIP> <interface>       
    * Performs arp spoofing with the passed parameters
    
--save, -s              <filename>
    * Tells the program to start saving all the packets that run through the system
    
--graph, -g             <chart_type>
    * Sets the program in graph mode where it collates information to create a graph
    
    #-- Chart_Types --#:
    All-Modes:
        
        0   -   Will show a bar graph with the total number of a packets' 
                protocol that the script has collected
                
        10  -   Will process a line graph with number of packets over time
        
        100 -   Displays an estimation on the number of retransmissions over time
            
    Packet Loss:
        
        1   -   Will show the packet loss percentage over time
        2   -   Shows total packets lost over time
            
    Bandwidth:
        
        1   -   Will show the rate of transfer over time
    """


class GraphDescription:
    """Used to hold descriptions for the graph types"""

    def __init__(self, effect_name, graph_number, description):
        self.effect_name = effect_name
        self.number = graph_number
        self.description = description


# Graphing Descriptions - It has to be present here to it can be counted as a valid graph number
graph_descriptions = [

    # None applies to All
    GraphDescription(None, 0, 'Bar graph collating the different packet protocols collected'),
    GraphDescription(None, 10, 'Line graph of Total Packets (No) X Time (s)'),
    GraphDescription(None, 100, 'TCP Retransmission Rate X Time (s)'),

    GraphDescription('PacketLoss', 1, 'Packet Loss (%) X Time (s)'),
    GraphDescription('PacketLoss', 2, 'Packets Lost (No) X Time (s)'),

    GraphDescription('Bandwidth', 1, 'Transfer Rate (B/s) X Time (s)')
]


edit_mode_descrptions = \
[
    # Number
    [1],

    # Desctiption
    ['TTL Incrementing']
]