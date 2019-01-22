from Effects.Bandwidth.BaseBandwidth import Bandwidth


class LimitBandwidth(Bandwidth):

    def __init__(   
                    self, 
                    bandwidth, 
                    accept_packets=True, 
                    show_output=True
                ):
        
        
        super().__init__(   
                            bandwidth=bandwidth,
                            accept_packets=accept_packets,
                            show_output=show_output
                        )

    def custom_effect(self, packet):
        """Used to limit the bandwidth rate"""

        # Check if rate is over the limit
        self.packet_backlog.append(packet)

        while self.rate < self.bandwidth and len(self.packet_backlog) > 0:
            self.send_packet(self.packet_backlog[0])

            self.calculate_rate_overall_avg()

            # Packet is removed from the list
            del self.packet_backlog[0]
