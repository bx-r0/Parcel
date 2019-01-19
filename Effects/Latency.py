from Effects.Effect import Effect
import time


"""
graph_type_num:

    0 - Default graph - Number of types of various packets

"""


class Latency(Effect):
    """Class that is used to issue latency degradation"""

    def __init__(self, latency_value,
                 accept_packets=True,
                 show_output=True,
                 graphing=False,
                 gather_stats=True,
                 graph_type_num=0):

        super().__init__(accept_packets=accept_packets,
                         show_output=show_output,
                         graphing=graphing,
                         gather_stats=gather_stats,
                         graph_type_num=graph_type_num)

        self.latency_value = latency_value / 1000
        self.print('[*] Latency set to: {}s'.format(self.latency_value), force=True)
        self.total_packets = 0

        # In seconds
        self.latency_max = 1

    def print_stats(self):
        self.print('[*] Latency: {:.0f}ms - Total Packets effected: {} '.
                   format((self.latency_value * 1000), self.total_packets), end='\r')

    def custom_effect(self, packet):
        """Thread functionality"""

        if type(packet) is list:
            packetObj = packet[0]
            startTime = packet[1]

            elapsed = time.time() - startTime
            wait_time = self.latency_value - elapsed

            if wait_time < 0:
                pass
            else:
                time.sleep(wait_time)

            self.accept(packetObj)
        else:
            time.sleep(self.latency_value)
            self.accept(packet)

    def alter_latency_value(self, new_value):
        """This is useful if latency isn't static and can be obtained from a range"""
        self.print('[*] Latency: {:.2f}s - '.format(new_value), end='')
        self.latency_value = new_value

    def increase_effect(self):
        """Called when the 'e' key is pressed"""
        increment_value = 0.01

        # Validation
        if (self.latency_value + increment_value) < self.latency_max:
            self.latency_value += increment_value

    def decrease_effect(self):
        """Called when the 'q' key is pressed"""
        decrement_value = 0.01

        # Validation - Checks if result would be non negative
        if (self.latency_value - decrement_value) > 0:
            self.latency_value -= decrement_value


