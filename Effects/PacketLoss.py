from Effects.Effect import Effect
from scapy.all import *


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

    # --- Graphing
    def graphing_setup(self):
        """Performs all the necessary setup"""

        # Tracks packet loss over time
        if self.graph_type_num is 1:
            self.graph.set_x_axis_label('Time (s)')
            self.graph.set_y_axis_label('Packet Loss (%)')

        # Total packets lost over time
        elif self.graph_type_num is 2:
            self.graph.set_x_axis_label('Time (s)')
            self.graph.set_y_axis_label('Individual Packets Lost (No Of Packets)')

    def graphing_effect(self, packet):
        """Performs the data collecting for the graph"""

        # Tracks packet loss over time
        if self.graph_type_num is 1:
            self.graph.add_points(self.get_elapsed_time(), self.dropped_percentage)

        # Total packets lost over time
        elif self.graph_type_num is 2:
            self.graph.add_points(self.get_elapsed_time(), self.dropped_packets)

    def show_custom_graph(self):
        """Shows the custom graphs for the packet loss effect"""

        # Percentage loss over time
        if self.graph_type_num is 1:
            self.graph.plot('r,-')

        # Total packets lost over time
        elif self.graph_type_num is 2:
            self.graph.plot('y,-')

    def increase_effect(self):
        """Called when the 'e' key is pressed"""
        increment_value = 1  # Changes by 1%

        # Validation
        if (self.packet_loss_percentage + increment_value) < 100:
            self.packet_loss_percentage += increment_value

    def decrease_effect(self):
        """Called when the 'q' key is pressed"""
        decrement_value = 1  # Changes by 1 %

        # Validation - Checks if result would be non negative
        if (self.packet_loss_percentage - decrement_value) > 0:
            self.packet_loss_percentage -= decrement_value
