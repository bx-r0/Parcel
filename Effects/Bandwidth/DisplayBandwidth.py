from Effects.Bandwidth.BaseBandwidth import Bandwidth


class DisplayBandwidth(Bandwidth):

    def __init__(self, accept_packets=True, show_output=True, graphing=False, gather_stats=False, graph_type_num=0):
        super().__init__(bandwidth=0,
                         accept_packets=accept_packets,
                         show_output=show_output,
                         graphing=graphing,
                         gather_stats=gather_stats,
                         graph_type_num=graph_type_num)

    def custom_effect(self, packet):
        """Used to display the bandwidth"""

        self.send_packet(packet)
