from Effects.Bandwidth.BaseBandwidth import Bandwidth


class DisplayBandwidth(Bandwidth):

    def __init__(
                    self, 
                    accept_packets=True, 
                    show_output=True
                ):
                
        super().__init__(
                            bandwidth=0,
                            accept_packets=accept_packets,
                            show_output=show_output
                        )

    def custom_effect(self, packet):
        """Used to display the bandwidth"""

        self.send_packet(packet)
