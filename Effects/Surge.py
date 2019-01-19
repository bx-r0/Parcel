from Effects.Effect import Effect
import threading
import time


class Surge(Effect):
    """Effect that groups together packets and sends them in one big group"""

    def __init__(self, period, accept_packet=True, show_output=True, graphing=False, graph_type_num=0):
        super().__init__(accept_packets=accept_packet,
                         show_output=show_output,
                         graphing=graphing,
                         graph_type_num=graph_type_num)

        # General vars
        self.packet_pool = []
        self.surge_job = None
        self.collection_period = period / 1000

        self.print('[*] Packet surge delay set to {}s'.format(self.collection_period), force=True)

    def custom_effect(self, packet):
        """General effect"""

        # HACK: Why is this wait needed?
        time.sleep(0.00001)
        self.packet_pool.append(packet)

    def surge_purge(self):
        """Event that purges the packet pool when the time has elapsed"""

        # Sends all packets!
        for x in self.packet_pool:
            self.accept(x)

        pool_len = len(self.packet_pool)

        self.print_clear()
        self.print("[!] Packets sent: {} - Surge Interval: {:.2f}s".format(pool_len, self.collection_period), end='\r')

        self.packet_pool = []
        self.start_purge_monitor()

    def start_purge_monitor(self):
        """Starts the timer that after the time period sends the batch of packets"""

        # Starts another thread
        self.surge_job = threading.Timer(self.collection_period, self.surge_purge).start()

    def stop(self):
        """Stops the purge monitor job"""

        self.surge_job.cancel()
        self.print('[!] Purge job stopped!')

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

    # -- Controls
    def increase_effect(self):
        interval = 0.1

        self.collection_period += interval

    def decrease_effect(self):
        interval = 0.1

        if (self.collection_period - interval) > 0:
            self.collection_period -= interval
