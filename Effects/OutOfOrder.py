from Effects.Effect import Effect
import threading
import random


class Order(Effect):

    def __init__(self, accept_packet=True, show_output=True, graphing=False, graph_type_num=0):
        super().__init__(accept_packets=accept_packet,
                         show_output=show_output,
                         graphing=graphing,
                         graph_type_num=graph_type_num)

        # General vars
        self.send_interval = 1
        self.packet_list = []
        self.total = 0
        self.packet_send_job = None

        self.start_packet_send()

    def print_stats(self):
        self.print('[*] Total packets received {}'.format(self.total), end='\r')

    def custom_effect(self, packet):
        # Saves the packet
        self.packet_list.append(packet)

    def send_packet(self):

        # Grabs a position in the list
        list_len = len(self.packet_list)

        # Sends and deletes from the list
        while list_len > 0:
            index = random.randint(0, list_len - 1)
            self.accept(self.packet_list[index])
            del self.packet_list[index]
            list_len = len(self.packet_list)

        self.start_packet_send()

    def start_packet_send(self):
        self.packet_send_job = threading.Timer(self.send_interval, self.send_packet).start()

    def stop(self):
        self.packet_send_job.stop()

    # --- Graphing
    def graphing_setup(self):
        """Performs the setup for the custom graphs"""
        pass

    def graphing_effect(self, packet):
        """Performs the data collecting for the graph"""
        pass

    def show_custom_graph(self):
        """Called to display any type of graph"""
        pass

