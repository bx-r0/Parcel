"""Changes made here will effect the parameters taken for each effect"""

cmd_latency = '-l'
cmd_packetloss = '-pl'
cmd_target_packet = '-tp'
cmd_print = '-p'
cmd_bandwidth = '-b'
cmd_throttle = '-t'
cmd_ratelimit = '-rl'
cmd_combination = '-c'
cmd_outoforder = '-o'
cmd_arp = '-a'
cmd_save = '-s'
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

--rate-limit, -rl   <rate_bytes>            
    * Limits the throughput of the program
                                
--combination, -c   <latency_ms> <packet-loss> <bandwidth_bytes>
    * Performs latency and packet loss at the same time
    
--out-of-order, -o 
    * Sets the mode to out of order that alters the order of incoming packets
    
## ---- Extra Optionals:

--target-packet, -tp    <packet-type>        
    * Only performs an affect on the specified packet type

--save, -s              <filename>
    * Tells the program to start saving all the packets that run through the system
    
"""
