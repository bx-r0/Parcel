from Effects.Effect import Effect
from Parameters import edit_mode_descrptions
from scapy.all import *
import sys


class Edit(Effect):

    def __init__(self, edit_type, accept_packets=True, show_output=True, graphing=False, graph_type_num=0):
        super().__init__(accept_packets=accept_packets,
                         show_output=show_output,
                         graphing=graphing,
                         graph_type_num=graph_type_num)

        # Defines which elements of the packet are changed
        self.edit_type = int(edit_type)
        self.edit_type_validation()

    def edit_type_validation(self):
        count = 0
        for edit_number in edit_mode_descrptions[0]:
            if edit_number is self.edit_type:
                description = edit_mode_descrptions[1][count]

                self.print('[*] Edit mode is set to: {} '.format(self.edit_type))
                self.print('[*]     Description \'{}\''.format(description))
                return
            count += 1

        # If none are found
        self.print('\n[ERROR] Incorrect edit type number!\n')
        sys.exit(0)

    def print_stats(self):
        self.print('[*] Packets edited: {}'.format(self.total_packets), end='\r')

    def custom_effect(self, packet):
        # Switch for modes
        if self.edit_type is 1:
            self.TTL_Incrementing(packet)

        #       <-- Add more modes here

    # Edit modes
    def TTL_Incrementing(self, packet):
        pkt = IP(packet.get_payload())

        # Increments the Time To Live of the packet
        pkt.ttl += 1

        # Recalculates the check sum
        del pkt[IP].chksum

        # Sets the packet to the modified version
        packet.set_payload(bytes(pkt))

        self.accept(packet)