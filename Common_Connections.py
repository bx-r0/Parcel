import random


class Connection:
    """Container Class for real world connection types"""

    def __init__(self, latency, packet_loss, bandwidth, name):

            # Loops through and checks parameter lengths
            incorrect = (x for x in [latency, packet_loss, bandwidth] if not self.check_parameters(x))
            for value in incorrect:
                raise Exception('Invalid parameters passed for Connection object: {}!'.format(value))

            self.latency = latency
            self.packet_loss = packet_loss
            self.bandwidth = bandwidth
            self.name = name

    @staticmethod
    def check_parameters(parameter):
        if len(parameter) is 2:
            return True
        else:
            return False

    def rnd_latency(self):
        return self.rnd(self.latency) / 1000

    def rnd_packet_loss(self):
        return int(self.rnd(self.packet_loss))

    def rnd_bandwidth(self):
        return int(self.rnd(self.bandwidth))

    @staticmethod
    def rnd(p_list):
        """Returns a random value in the given range"""

        low = p_list[0]
        high = p_list[1]

        return random.randint(low, high)


# References for values
# 3G and 4G
#   https://www.ofcom.org.uk/about-ofcom/latest/media/media-releases/2014/3g-4g-bb-speeds

# Wifi
#   https://www.ispreview.co.uk/index.php/2017/04/ofcom-2017-study-average-uk-home-broadband-speeds-rise-36-2mbps.html

# Hard coded real-world values
# The values are specified as lists representing ranges

_3G = Connection(
    latency=[53, 86],
    bandwidth=[1600000, 1700000],
    packet_loss=[1, 2],
    name='3G')

_4G = Connection(
    latency=[47, 62],
    bandwidth=[10400000, 18400000],
    packet_loss=[0.5, 1],
    name='4G')

_WIFI = Connection(
    latency=[30, 40],
    bandwidth=[30000000, 36000000],
    packet_loss=[0, 1],
    name='WIFI')

_NoConnection = Connection(
    latency=[0, 0],
    bandwidth=[0, 0],
    packet_loss=[100, 100],
    name='NoConnection')


# List of connection types
connections = \
    [
        _3G,
        _4G,
        _WIFI,
        _NoConnection
    ]

