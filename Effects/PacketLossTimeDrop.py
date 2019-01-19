import time
from Effects.Effect import Effect
from scapy.all import *

class PacketLossTimeDrop(Effect):

    def __init__(self, drop_interval,
                 accept_packets=True,
                 show_output=True,
                 graphing=False,
                 gather_stats=True,
                 graph_type_num=False):

        super().__init__(accept_packets=accept_packets,
                         show_output=show_output,
                         graphing=graphing,
                         gather_stats=gather_stats,
                         graph_type_num=graph_type_num)

        # Stats
        self.total_packets = 0
        self.time_since_last_drop = -1

        self.DROP_INTERVAL_SECONDS = drop_interval

    def custom_effect(self, packet):
        """This function will issue packet loss,
           a percentage is defined and anything
           lower is dropped and anything higher is accepted"""

        # This is the default port for Iperf
        INCOMMING_PORT = 5001

        # Initial set
        if self.time_since_last_drop is -1:
            self.time_since_last_drop = time.time()
            self.accept(packet)
        else:
            elapsed = time.time() - self.time_since_last_drop

            if elapsed > self.DROP_INTERVAL_SECONDS:

                try:
                    pkt = IP(packet.get_payload())
                    if pkt.sport is not INCOMMING_PORT:
                        self.time_since_last_drop = time.time()
                        packet.drop()
                except:
                    pass
            else:
                self.accept(packet)

    def print_stats(self):
        self.print("[*] " + str(self.total_packets), end='\r')