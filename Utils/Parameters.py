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
EFFECTS
Only one effect can be selected 

    -p                      Prints all the packets
    -i                      Does nothing to the packets. Used to show how much default overhead there is
    -b                      Displays information on the transfer rate
    -l    <delay_ms>        Applies latency on the connection   
    -pl   <percentage>      Performs packet loss on the connection
    -t    <delay_ms>        Creates a packet surge on a connection by the given delay 
    -rl   <rate_bytes>      Limits the throughput of the program
        
    OPTIONS 
    Can be used with any effect

    -tp   <packet-type>     Only performs an effect on the specified packet type
    -s   <filename>         Saves all collected packets into a .pcap file

"""
