import time
from scapy.layers.inet import IP
from Utils.Terminal import Terminal

class Effect:
    """Class that generally defines what an effect should contain

    Params
        accept_packets  - Defines if packets should be accepted (Used when stringing effects together)
        show_output     - Says if the effect should show any output
        graphing        - Toggles if the effect should collect data for a graph
        gather_stats    - Switches on or off the data collection for packets like tcp
        graph_type_num  - Defines the different graph to be generated. List in the the usage menu
    """

    def __init__(
                    self,
                    accept_packets=True,
                    show_output=True,
                    slimline=False
                ):

        self.total_packets = 0
        self.accept_packet = accept_packets
        self.show_output = show_output
        self.slimline = slimline

    def effect(self, packet):
        """The first method run for all effects - Here custom code will be added
        to collate information"""

        try:
            self.total_packets += 1
            self.print_stats()
            self.custom_effect(packet)
        except Exception as e:
            print('Error in effect(): ', e)

    def custom_effect(self, packet):
        """Each effect will need it's own custom effect"""
        raise Exception('NotImplemented: Please add \'custom_effect()\' to your class')

    def print_stats(self):
        """[Blueprint] - Should print the custom stats for each method.
        Note Print_stats should call 'self.print()' to show any output """
        pass

    def print(self, message, end='\n', force=False):
        """General print method"""
        if self.show_output or force:
            print(message, end=end, flush=True)

    @staticmethod
    def print_clear():
        """Method that is used to clear the output line, this is
        so no fragments are left after a stat print refresh"""
        Terminal.clear_line()

    def accept(self, packet):
        """Center point for accepting packets"""
        if self.accept_packet:
            packet.accept()

    def stop(self):
        """[Blueprint] - Called to stop the object"""
        pass

    def check_packet_type(self, packet, target_packet):
        """Checks if the packet is of a certain type"""

        # Grabs the first section of the Packet
        packet_string = str(packet)
        split = packet_string.split(' ')

        # Checks for the target packet type
        if target_packet == split[0]:
            return True
        else:
            return False
