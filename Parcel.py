# User created imports
from Effects import Print, OutOfOrder, Surge, PacketLoss, Latency
from Effects.Bandwidth import DisplayBandwidth, LimitBandwidth

import Utils.Parameters as Parameter
from Utils.Terminal import Terminal

# Dependencies
from scapy.all import PcapWriter
from scapy.layers.inet import IP
import netfilterqueue

from multiprocessing.pool import ThreadPool as Pool
import subprocess
import threading
import argparse
import textwrap
import logging
import signal
import time
import sys
import os

# Suppresses the Scapy WARNING Message
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Defines how many threads are in the pool
pool = Pool(2000)

# Terminal Sizing
terminal_height, terminal_width = os.popen('stty size', 'r').read().split()


def start_timer():
    """Keeps track of elapsed time"""

    global time_start
    time_start = time.time()


def get_time_in_secconds():
    now = time.time()
    elapsed = now - time_start
    return elapsed


def map_thread(method, args):
    """Method that deals with the threading of the packet manipulation"""

    # If this try is caught, it occurs for every thread active so anything in the
    # except is triggered for all active threads
    try:
        pool.map_async(method, args)
    except Exception as e:
        print(e)


def print_force(message):
    """This method is required because when this python file is called as a script
    the prints don't appear and a flush is required """
    print(message, flush=True)


def affect_packet(packet):
    """This function checks if the packet should be affected or not. This is part of the -t option"""

    # Saving packets
    if save_active:
        pktdump.write(IP(packet.get_payload()))

    if target_packet_type == "ALL":
        return True
    else:
        return check_packet_type(packet, target_packet_type)


def check_packet_type(packet, target_packet):
    """Checks if the packet is of a certain type"""

    # Grabs the first section of the Packet
    packet_string = str(packet)
    split = packet_string.split(' ')

    # Checks for the target packet type
    if target_packet == split[0]:
        return True
    else:
        return False


def external(packet):
    """This method is used to run the effect of a script
    from another script"""
    if affect_packet(packet):
        map_thread(external_obj.effect, [packet])
    else:
        packet.accept()


def print_packet(packet):
    """This function just prints the packet"""

    if affect_packet(packet):
        map_thread(effectObject.effect, [packet])
    else:
        packet.accept()


def ignore_packet(packet):
    """Used to test the overhead of moving packets through the NFQUEUE"""

    packet.accept()


def packet_latency(packet):
    """This function is used to incur latency on packets"""
    if affect_packet(packet):
        map_thread(effectObject.effect, [[packet, time.time()]])
    else:
        packet.accept()


def packet_loss(packet):
    """Function that performs packet loss on all packets"""
    if affect_packet(packet):
        map_thread(effectObject.effect, [packet])
    else:
        packet.accept()


def surge(packet):
    """Mode assigned to send packets in a surge"""
    if affect_packet(packet):
        effectObject.effect(packet)
    else:
        packet.accept()


def track_bandwidth(packet):
    """This mode allows for the tracking of rate of packets recieved"""
    if affect_packet(packet):
        effectObject.effect(packet)
    else:
        packet.accept()


def limit_bandwidth(packet):
    """This is mode for limiting the rate of transfer"""
    if affect_packet(packet):
        effectObject.effect(packet)
    else:
        packet.accept()


def out_of_order(packet):
    """Mode that alters the order of packets"""
    if affect_packet(packet):
        effectObject.effect(packet)
    else:
        packet.accept()


def setup_packet_save(filename):
    """Sets up a global object that is used to save the files
    to a .pcap file"""

    global pktdump
    pktdump = PcapWriter(filename + '.pcap', append=False, sync=True)


def run_packet_manipulation_external(external_object, target_packet='ALL'):
    """This method allows the script to be run from another script
    it skips the parameter checking and allows for a custom object to be passed and run"""

    global mode, external_obj, target_packet_type, save_active, NFQUEUE_Active

    # Sets the target packet
    target_packet_type = target_packet
    save_active = False
    NFQUEUE_Active = True

    external_obj = external_object
    mode = external

    run_packet_manipulation()


def run_packet_manipulation():
    """The main method here, will issue a iptables command and construct the NFQUEUE"""

    try:
        global nfqueue

        # Packets for this machine
        os.system("iptables -A INPUT -j NFQUEUE")

        # Packets created from this machine
        os.system("iptables -A OUTPUT -j NFQUEUE")

        # Packets for forwarding or other routes
        os.system("iptables -A FORWARD -j NFQUEUE")

        print_force("[*] Mode is: " + mode.__name__)

        # Setup for the NQUEUE
        nfqueue = netfilterqueue.NetfilterQueue()

        try:
            nfqueue.bind(0, mode)  # 0 is the default NFQUEUE
        except OSError:
            print_force("[!] Queue already created")

        # Shows the start waiting message
        print_separator()
        print_force("[*] Waiting ")
        nfqueue.run()

    except KeyboardInterrupt:
        clean_close()


def parameters():
    """This function deals with parameters passed to the script"""

    # Defines globals to be used above
    global mode, effectObject, target_packet_type, save_active, NFQUEUE_Active

    # Defaults
    mode = print_packet
    target_packet_type = 'ALL'
    save_active = False

    # Setup
    start_timer()
    NFQUEUE_Active = True

    # Arguments
    parser = argparse.ArgumentParser(prog="Packet.py",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     allow_abbrev=False)

    parser.add_argument_group('Arguments', description=Parameter.Usage())

    # Mode parameters
    effect = parser.add_mutually_exclusive_group(required=True,)

    effect.add_argument('--print', Parameter.cmd_print,
                        action='store_true',
                        help=argparse.SUPPRESS)

    effect.add_argument('--ignore', '-i',
                        action='store_true',
                        dest='ignore',
                        help=argparse.SUPPRESS)

    effect.add_argument('--latency', Parameter.cmd_latency,
                        action='store',
                        help=argparse.SUPPRESS,
                        type=int)

    effect.add_argument('--packet-loss', Parameter.cmd_packetloss,
                        action='store',
                        help=argparse.SUPPRESS,
                        type=int)

    effect.add_argument('--surge', Parameter.cmd_throttle,
                        action='store',
                        help=argparse.SUPPRESS,
                        type=int)

    effect.add_argument('--display-bandwidth', Parameter.cmd_bandwidth,
                        action='store_true',
                        help=argparse.SUPPRESS)

    effect.add_argument('--rate-limit', Parameter.cmd_ratelimit,
                        action='store',
                        dest='rate_limit',
                        help=argparse.SUPPRESS,
                        type=int)

    # Extra parameters
    parser.add_argument('--target-packet', Parameter.cmd_target_packet,
                        action='store',
                        help=argparse.SUPPRESS)

    parser.add_argument('--save', Parameter.cmd_save,
                        nargs=1,
                        dest='save',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Modes
    if args.print:

        effectObject = Print.Print()
        mode = print_packet

    elif args.ignore:
        mode = ignore_packet

    elif args.latency:
        effectObject = Latency.Latency(latency_value=args.latency)
        mode = packet_latency

    elif args.packet_loss:
        effectObject = PacketLoss.PacketLoss(percentage=args.packet_loss)
        mode = packet_loss

    elif args.surge:
        effectObject = Surge.Surge(period=args.surge)
        effectObject.start_purge_monitor()
        mode = surge

    elif args.display_bandwidth:
        effectObject = DisplayBandwidth.DisplayBandwidth()
        mode = track_bandwidth

    elif args.rate_limit:
        # Sets the bandwidth object with the specified bandwidth limit
        effectObject =LimitBandwidth.LimitBandwidth(bandwidth=args.rate_limit)
        mode = limit_bandwidth

    if args.save:
        print_force(
            '[!] File saving on - Files will be saved under: \'{}.pcap\''.format(args.save[0]))

        save_active = True
        setup_packet_save(args.save[0])

    # When all parameters are handled
    if NFQUEUE_Active:
        run_packet_manipulation()


def clean_close(signum='', frame=''):
    """Used to close the script cleanly"""

    print_force('\n')
    print_force("[*] ## Close signal recieved ##")
    effectObject.stop()

    try:
        if NFQUEUE_Active:

            pool.close()
            print_force("[!] Thread pool killed")

            # Resets
            print_force("[!] iptables reverted")
            os.system("iptables -F")

            print_force("[!] NFQUEUE unbinded")
            nfqueue.unbind()

            if arp_active:
                print_force('[!] Arp Spoofing stopped!')
                arp_process.terminate()

            print_force('[!] ## Script Stopped ##')
    except NameError:
        pass

    os._exit(0)


def print_separator():
    Terminal.print_sequence('=', start='[*]', end='[*]')


# Rebinds the all the close signals to clean_close the script
signal.signal(signal.SIGINT, clean_close)   # Ctrl + C
signal.signal(signal.SIGQUIT, clean_close)  # Ctrl + \
signal.signal(signal.SIGTSTP, clean_close)  # Ctrl + Z

# Check if user is root
if os.getuid() != 0:
    exit("Error: User needs to be root to run this script")


if __name__ == "__main__":
    print_separator()
    parameters()
