from Effects.Effect import Effect
import threading
import time


class Bandwidth(Effect):
    """
    Class that deals with bandwidth functionality
    - Bandwidth (rate limiting)
    - Displaying Bandwidth
    """

    def __init__(
                    self, bandwidth=0,
                    accept_packets=True,
                    show_output=True
                ):

        super().__init__(
                            accept_packets=accept_packets,
                            show_output=show_output
                        )

        # Constants
        self.units = ['B', 'KB', 'MB', 'GB']

        # General variables
        self.total_size = 0
        self.transferred_since_check = 0
        self.rate = 0
        self.packet_backlog = []

        # Time variables
        self.previous = time.time()
        self.start = time.time()

        # # CHARACTERISTICS # #
        # Can be changed
        self.rate_update_period = 1  # In seconds

        self.bandwidth = bandwidth
        if bandwidth is not 0:
            self.print('[*] Bandwidth set to: {} B/s'.format(bandwidth), force=True)

        self.start_rate_update()

    def print_stats(self):
        """Stat output"""

        # Displays totals and rate in more relevant units
        print_rate, unit_rate = self.recalculate_units(self.rate)
        print_total, unit_total = self.recalculate_units(self.total_size)

        # Stops any stray characters
        self.print_clear()

        print_message = '[*] Total: {:.1f} {} - Rate: {:.1f} {}/s '

        # If the rate limiting is on
        if self.bandwidth is not 0:

            print_message += "- Target Rate {:.1f}B/s"

            self.print(print_message.format(print_total, unit_total, print_rate, unit_rate, self.bandwidth), end='\r')

        # If it is just displaying bandwidth
        else:
            self.print(print_message.format(print_total, unit_total, print_rate, unit_rate), end='\r')

    def calculate_rate_job(self):
        """Calculates the rate of throughput"""

        if self.bandwidth is 0:
            self.calculate_rate()
        else:
            self.calculate_rate_overall_avg()

        self.start_rate_update()

    def calculate_rate(self):
        # Const variable that is the period of time the rate is calculated over
        # Measured in seconds
        now = time.time()
        elapsed = (now - self.previous)

        # Refresh rate
        if elapsed > self.rate_update_period:
            self.rate = (self.transferred_since_check / elapsed)

            self.print_stats()

            # Reset
            self.transferred_since_check = 0
            self.previous = now

    def calculate_rate_overall_avg(self):
        """Used to calculate the rate as an overall average"""

        now = time.time()
        elapsed = now - self.start

        self.rate = self.total_size / elapsed
        self.print_stats()

    @staticmethod
    def calculate_packet_size(packet_name):
        """Grabs the size of the packet from the name of the packet"""

        # Packet format
        #   '<Name> packet <Size> Bytes'
        parts = str(packet_name).split(' ')
        packet_size = parts[-2]
        return int(packet_size)

    def recalculate_units(self, value):
        """Recalculates the units when they flow over.
        For example KBs -> MBs """

        times_reduced = 0
        unit = self.units[times_reduced]

        # Increase
        while value > 1000 and times_reduced < 3:
            value = value / 1000
            times_reduced += 1
            unit = self.units[times_reduced]

        # Decrease
        while value < 0.1 and times_reduced > 0:
            value = value * 1000
            times_reduced -= 1
            unit = self.units[times_reduced]

        return value, unit

    def send_packet(self, packet):
        """Sends a packet and increases the total"""
        packet_size = self.calculate_packet_size(packet)

        self.total_size += packet_size
        self.transferred_since_check += packet_size

        self.accept(packet)

    def start_rate_update(self):
        """Used to start the thread that updates the rate of transfer"""
        threading.Timer(self.rate_update_period, self.calculate_rate_job).start()

    def alter_bandwidth(self, new_value):
        """Used to change bandwidth variable for an outside location"""
        self.bandwidth = new_value