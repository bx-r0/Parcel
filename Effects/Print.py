from Effects.Effect import Effect
from scapy.all import *

class Print(Effect):

    def __init__(self, accept_packets=True, show_output=True, graphing=False, graph_type_num=0):
        super().__init__(accept_packets=accept_packets,
                         show_output=show_output,
                         graphing=graphing,
                         graph_type_num=graph_type_num)

    def custom_effect(self, packet):

        pkt = IP(packet.get_payload())

        src = pkt[IP].src
        dst = pkt[IP].dst

        print('[!] {0:<25} Src: {1:<15} Dst: {2:<15}'.format(str(packet), src, dst), flush=True)

        self.accept(packet)
