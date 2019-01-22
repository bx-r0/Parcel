from Effects.Effect import Effect
import time

class Latency(Effect):
    """Class that is used to issue latency degradation"""

    def __init__(
                    self, 
                    latency_value,
                    accept_packets=True,
                    show_output=True
                ):

        super().__init__(
                            accept_packets=accept_packets,
                            show_output=show_output
                        )

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

        if isinstance(packet, list):
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
