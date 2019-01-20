from Effects.Effect import Effect
import random

class PacketLoss(Effect):

    def __init__(self, percentage,
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

        self.packet_loss_percentage = int(percentage)
        self.print('[*] Packet loss set to: {}%'.format(percentage), force=True)

        # Stats
        self.total_packets = 0
        self.dropped_packets = 0
        self.dropped_percentage = 0

    def print_stats(self):
        if not self.total_packets == 0:
            self.dropped_percentage = (self.dropped_packets / self.total_packets) * 100
        else:
            self.dropped_percentage = 0

        self.print("[*] Total Packets: {} - "
                   "Target Loss {:.0f}% - "
                   "Actual Loss {:.2f}%"

            .format(self.total_packets,
                    self.packet_loss_percentage,
                    self.dropped_percentage), end='\r')

    def alter_percentage(self, new_value):
        self.print('Packet loss: {}% -- '.format(new_value), end='')
        self.packet_loss_percentage = new_value

    def custom_effect(self, packet):
        """This function will issue packet loss,
           a percentage is defined and anything
           lower is dropped and anything higher is accepted"""

        if self.packet_loss_percentage != 0:

            # random value from 0 to 100
            random_value = random.uniform(0, 100)

            # If the generated value is smaller than the percentage discard
            if self.packet_loss_percentage > random_value:
                self.dropped_packets += 1
                packet.drop()

            # Accept the packet
            else:
                self.accept(packet)
        else:
            self.accept(packet)
