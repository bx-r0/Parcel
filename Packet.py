#region Imports
# Import graphing
import matplotlib as mpl
if __name__ == "__main__":
    mpl.use('Agg')

# Suppresses the Scapy WARNING Message
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# General Imports
import argparse
import signal
import time
import threading
import textwrap
import Common_Connections
from Terminal import Terminal

from netfilterqueue import NetfilterQueue
from scapy.all import *
from multiprocessing.pool import ThreadPool as Pool
import keyboard

# Module imports
import Parameters as Parameter

from Effects import *

from Effects.Latency import Latency
from Effects.Bandwidth.LimitBandwidth import LimitBandwidth
from Effects.Bandwidth.DisplayBandwidth import DisplayBandwidth
from Effects.PacketLoss import PacketLoss
from Effects.Surge import Surge
from Effects.OutOfOrder import Order
from Effects.Print import Print
from Effects.EditPacket import Edit
from Effects.Attacks.UDP_Flooding import UDP_Flood
from Effects.Attacks.ARP_Spamming import ARP_Spamming
from Plotting import Graph
#endregion

# Defines how many threads are in the pool
pool = Pool(2000)

logo = """
==============================================================
Degraded Packet Simulation

    ██████╗ ██████╗ ███████╗
    ██╔══██╗██╔══██╗██╔════╝
    ██║  ██║██████╔╝███████╗
    ██║  ██║██╔═══╝ ╚════██║
    ██████╔╝██║     ███████║
    ╚═════╝ ╚═╝     ╚══════╝
"""

epilog = """
Aidan Fray
afray@hotmail.co.uk

==============================================================
"""

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
        map_thread(print_obj.effect, [packet])
    else:
        packet.accept()


def ignore_packet(packet):
    """Used to test the overhead of moving packets through the NFQUEUE"""

    packet.accept()


def edit_packet(packet):
    """This function will be used to edit sections of a packet, this is currently incomplete"""

    if affect_packet(packet):
        map_thread(edit_obj.effect, [packet])
    else:
        packet.accept()


def packet_latency(packet):
    """This function is used to incur latency on packets"""
    if affect_packet(packet):
        map_thread(latency_obj.effect, [[packet, time.time()]])
    else:
        packet.accept()


def packet_loss(packet):
    """Function that performs packet loss on all packets"""
    if affect_packet(packet):
        map_thread(packet_loss_obj.effect, [packet])
    else:
        packet.accept()


def surge(packet):
    """Mode assigned to send packets in a surge"""
    if affect_packet(packet):
        throttle_obj.effect(packet)
    else:
        packet.accept()


def combination(packet):
    """This performs effects together"""
    packet_loss_obj.effect(packet)
    latency_obj.effect(packet)
    bandwidth_obj.effect(packet)


def combination_effect(packet):
    """The effect of having multiple effects on a """
    if affect_packet(packet):
        map_thread(combination, [packet])
    else:
        packet.accept()


def emulate_real_connection_speed(packet):
    """Used to emulate real world connections speeds"""
    global connection

    if affect_packet(packet):

        rnd_latency = connection.rnd_latency()
        rnd_packet_loss = connection.rnd_packet_loss()
        rnd_bandwidth = connection.rnd_bandwidth()

        print('[*] Current values: L: {}s P: {}% B: {}B/s '.format(rnd_latency, rnd_packet_loss, rnd_bandwidth), end='\r')

        # Adjusts the values
        latency_obj.alter_latency_value(rnd_latency)
        packet_loss_obj.alter_percentage(rnd_packet_loss)
        bandwidth_obj.alter_bandwidth(rnd_bandwidth)

        # Calls mode
        map_thread(combination, [packet])
    else:
        packet.accept()


def track_bandwidth(packet):
    """This mode allows for the tracking of rate of packets recieved"""
    if affect_packet(packet):
        bandwidth_obj.effect(packet)
    else:
        packet.accept()


def limit_bandwidth(packet):
    """This is mode for limiting the rate of transfer"""
    if affect_packet(packet):
        bandwidth_obj.effect(packet)
    else:
        packet.accept()


def out_of_order(packet):
    """Mode that alters the order of packets"""
    if affect_packet(packet):
        order_obj.effect(packet)
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

    global mode, external_obj, target_packet_type, arp_active, save_active, NFQUEUE_Active

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
        nfqueue = NetfilterQueue()

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
    global mode, target_packet_type, arp_active, save_active, NFQUEUE_Active

    global \
        latency_obj, \
        throttle_obj, \
        packet_loss_obj, \
        bandwidth_obj, \
        order_obj, \
        print_obj, \
        edit_obj, \
        udp_obj, \
        arp_spam_obj, \
        external_obj

    latency_obj = None
    throttle_obj = None
    packet_loss_obj = None
    bandwidth_obj = None
    order_obj = None
    print_obj = None
    edit_obj = None
    udp_obj = None
    arp_spam_obj = None

    # Defaults
    mode = print_packet
    target_packet_type = 'ALL'
    arp_active = False
    save_active = False
    graph_active = False

    # Setup
    start_timer()
    NFQUEUE_Active = True

    # Arguments
    parser = argparse.ArgumentParser(prog="Packet.py",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent(logo),
                                     epilog=textwrap.dedent(epilog),
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

    effect.add_argument('--combination', Parameter.cmd_combination,
                        action='store',
                        nargs=3,
                        help=argparse.SUPPRESS,
                        type=int)

    effect.add_argument('--simulate', Parameter.cmd_simulate,
                        action='store',
                        help=argparse.SUPPRESS)

    effect.add_argument('--display-bandwidth', Parameter.cmd_bandwidth,
                        action='store_true',
                        help=argparse.SUPPRESS)

    effect.add_argument('--rate-limit', Parameter.cmd_ratelimit,
                        action='store',
                        dest='rate_limit',
                        help=argparse.SUPPRESS,
                        type=int)

    effect.add_argument('--out-of-order', Parameter.cmd_outoforder,
                        action='store_true',
                        dest='order',
                        help=argparse.SUPPRESS)

    effect.add_argument('--edit-packets', Parameter.cmd_edit,
                        action='store',
                        dest='edit',
                        help=argparse.SUPPRESS)

    # Attacks
    effect.add_argument('--udp-flood', Parameter.cmd_flood,
                        action='store',
                        nargs=1,
                        dest='flood',
                        help=argparse.SUPPRESS)

    effect.add_argument('--arp-spam', Parameter.cmd_arp_spam,
                        action='store_true',
                        dest='arp_spam',
                        help=argparse.SUPPRESS)

    # Extra parameters
    parser.add_argument('--target-packet', Parameter.cmd_target_packet,
                        action='store',
                        help=argparse.SUPPRESS)

    parser.add_argument('--arp', Parameter.cmd_arp,
                        action='store',
                        nargs=3,
                        help=argparse.SUPPRESS)

    parser.add_argument('--save', Parameter.cmd_save,
                        nargs=1,
                        dest='save',
                        help=argparse.SUPPRESS)

    parser.add_argument('--graph', Parameter.cmd_graph,
                        action='store',
                        dest='graph',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    graph_type_num = 0
    if args.graph:
        print_force('[!] Graphing is on, press \'g\' at any point while running to display the graph')
        graph_active = True
        graph_type_num = int(args.graph)

    # Modes
    if args.print:
        print_obj = Print(graphing=graph_active,
                          graph_type_num=graph_type_num)
        mode = print_packet

    elif args.ignore:
        mode = ignore_packet

    elif args.latency:
        latency_obj = Latency(latency_value=args.latency,
                              graphing=graph_active,
                              graph_type_num=graph_type_num)
        mode = packet_latency

    elif args.packet_loss:
        packet_loss_obj = PacketLoss(percentage=args.packet_loss,
                                     graphing=graph_active,
                                     graph_type_num=graph_type_num)
        mode = packet_loss

    elif args.surge:
        throttle_obj = Surge(period=args.surge)
        throttle_obj.start_purge_monitor()
        mode = surge

    elif args.combination:
        latency_obj = Latency(latency_value=args.combination[0], accept_packets=False, show_output=False)
        bandwidth_obj = LimitBandwidth(bandwidth=args.combination[2], accept_packets=False, show_output=False)
        packet_loss_obj = PacketLoss(percentage=args.combination[1], accept_packets=True)
        mode = combination_effect

    elif args.simulate:
        global connection

        # Checks if the parameter is a valid connection
        connection = None
        for c in Common_Connections.connections:
            if c.name == str(args.simulate):
                connection = c

        # Could not find connection type
        if connection is None:
            print('Error: Could no find the \'{}\' connection entered'.format(args.simulate))
            sys.exit(0)

        # Prints a summary table for the connection speed
        print_force('[*] Connection type is emulating: {}'.format(connection.name))
        print_force('[*] ------------------------------------------- [*]')
        print_force('[*] Latency:       {}ms -> {}ms'.format(connection.latency[0], connection.latency[1]))
        print_force('[*] Packet Loss:   {}% -> {}%'.format(connection.packet_loss[0], connection.packet_loss[1]))
        print_force('[*] Bandwidth:     {}B/s -> {}B/s'.format(connection.bandwidth[0], connection.bandwidth[1]))
        print_force('[*] ------------------------------------------- [*]')

        latency_obj = Latency(latency_value=0, accept_packets=False, gather_stats=False, show_output=False)
        bandwidth_obj = LimitBandwidth(bandwidth=0, accept_packets=False, gather_stats=False, show_output=False)
        packet_loss_obj = PacketLoss(percentage=0, accept_packets=True, gather_stats=False, show_output=False)
        mode = emulate_real_connection_speed

    elif args.display_bandwidth:
        bandwidth_obj = DisplayBandwidth(graphing=graph_active,
                                         graph_type_num=graph_type_num)
        mode = track_bandwidth

    elif args.rate_limit:
        # Sets the bandwidth object with the specified bandwidth limit
        bandwidth_obj = LimitBandwidth(bandwidth=args.rate_limit,
                                  graphing=graph_active,
                                  graph_type_num=graph_type_num)
        mode = limit_bandwidth

    elif args.order:
        order_obj = Order(graphing=graph_active,
                          graph_type_num=graph_type_num)
        mode = out_of_order

    elif args.edit:
        edit_obj = Edit(edit_type=args.edit,
                        graphing=graph_active,
                        graph_type_num=graph_type_num)

        mode = edit_packet

    # --- Attacks
    elif args.flood:
        NFQUEUE_Active = False
        udp_obj = UDP_Flood(args.flood[0])
        udp_obj.start()

    elif args.arp_spam:
        NFQUEUE_Active = False
        arp_spam_obj = ARP_Spamming()
        arp_spam_obj.start()

    # Extra settings
    if args.target_packet:
        local_args = args.target_packet

        target_packet_type = local_args
        print_force('[!] Only affecting {} packets'.format(target_packet_type))

    if args.arp:
        global arp_process

        local_args = args.arp

        print_force("[*] ## ARP spoofing mode activated ## ")

        victim = local_args[0]
        router = local_args[1]
        interface = local_args[2]

        filepath = os.path.dirname(os.path.abspath(__file__))

        # Runs the arp spoofing
        arp_active = True
        cmd = ['pkexec', 'python', filepath + '/ArpSpoofing.py']
        cmd = cmd + ['-t', victim, '-r', router, '-i', interface]
        arp_process = subprocess.Popen(cmd)

    if args.save:
        print_force('[!] File saving on - Files will be saved under: \'{}.pcap\''.format(args.save[0]))

        save_active = True
        setup_packet_save(args.save[0])

    # Starts the listener thread for user input
    threading.Thread(target=user_input_thread, args=[graph_active]).start()

    # When all parameters are handled
    if NFQUEUE_Active:
        run_packet_manipulation()


def affect_all_objects(method):
    """This method attempts to stop an object, and
    catches the exception if it doesn't need closing"""
    try:
        # TODO: Dynamic way to grab these?
        objects = [latency_obj, packet_loss_obj, throttle_obj, bandwidth_obj, order_obj, print_obj, udp_obj]

        for x in objects:

                # Add more functionality to this list
                if method is 'stop':
                    x.stop()
                elif method is 'graph':
                    x.show_graph()
                elif method is 'graph_no_show':
                    x.save_graph()
                elif method is 'increase':
                    x.increase_effect()
                elif method is 'decrease':
                    x.decrease_effect()
                else:
                    Exception('Invalid entry into affect_all_objects()')
    except AttributeError:
        pass
    except NameError:
        pass


def user_input_thread(graph_active):
    """This thread is a listener for users input"""

    def reset_cursor(msg):
        """Used to stop input from messing up terminal format
        and displays what command was entered"""

        Terminal.clear_line()
        print('[{}]'.format(msg), end='\r', flush=True)

    while True:

        # HACK: Stops this from looping too fast and soaking up to much performance
        # A better solution would be to introduce events
        time.sleep(0.01)

        try:
            if keyboard.is_pressed('g'):
                # Waits until the key is released
                while keyboard.is_pressed('g'):
                    pass

                if graph_active:
                    # Clears any fragments from the screen including the button pressed
                    Terminal.clear_line()
                    affect_all_objects('graph')
                reset_cursor('Show graph')

            # More degradation
            elif keyboard.is_pressed('e'):
                # Waits until the key is released
                while keyboard.is_pressed('e'):
                    pass
                affect_all_objects('increase')
                reset_cursor('Increase Effect')

            # Less degradation
            elif keyboard.is_pressed('q'):
                # Waits until the key is released
                while keyboard.is_pressed('q'):
                    pass
                affect_all_objects('decrease')
                reset_cursor('Decrease Effect')

        except RuntimeError:
            pass


def clean_close(signum='', frame=''):
    """Used to close the script cleanly"""

    print_force('\n')
    print_force("[*] ## Close signal recieved ##")
    affect_all_objects('stop')

    try:
        if NFQUEUE_Active:

            affect_all_objects('graph_no_show')

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
