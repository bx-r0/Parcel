import fcntl
import os
import subprocess
import gi
import signal
import queue
import _thread
import Common_Connections as Connection

from LocalNetworkScan import *
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
import GUI.Controls as Control
import Parameters as Parameter
import Plotting

# Add to this list to add or remove filters for the packet manipulation
target_protcols = ['TCP', 'UDP', 'ICMP']

# Gets the directory of the current file
filepath = os.path.dirname(os.path.abspath(__file__))


def ignore(signum, frame):
    """Method used to rebind close signals when performed on the terminal"""
    print('Signal: {} Ignored!'.format(signum))


# Rebinds the all the close signals to clean_close the script
signal.signal(signal.SIGINT, ignore)  # Ctrl + C
signal.signal(signal.SIGTSTP, ignore)  # Ctrl + Z
signal.signal(signal.SIGQUIT, ignore)  # Ctrl + \

class PacketCaptureGTK:
    """A GUI for controlling the Packet.py script"""

    # Loads and shows the window
    def __init__(self):
        self.running = False
        self.main_window_init()
        self.arp_window_init()
        Gtk.main()

    def main_window_init(self):
        # Creates the builder and loads the UI from the glade file
        builder = Gtk.Builder()
        builder.add_from_file("GUI/PacketCaptureWindow.glade")
        builder.connect_signals(self)

        self.mainWindow = builder.get_object("window1")
        self.mainWindow.show_all()

        # Buttons
        self.buttons = {}
        self.add_controls(builder, self.buttons, Control.buttons_values)

        # TextBoxes
        self.textBoxes = {}
        self.add_controls(builder, self.textBoxes, Control.textbox_values)

        # TextViews
        self.textViews = {}
        self.add_controls(builder, self.textViews, Control.textview_values)

        # Combo Box
        self.checkBox_packetFilter = builder.get_object("CheckBox_PacketFilter")
        self.comboBox_packetFilter = builder.get_object("ComboBox_PacketFilter")
        iface_list_store = Gtk.ListStore(GObject.TYPE_STRING)
        for item in target_protcols:  # Creates the lists
            iface_list_store.append([item])
        self.comboBox_packetFilter.set_model(iface_list_store)
        self.comboBox_packetFilter.set_active(0)

        # Test
        self.textbuffer_console = self.textViews['TextView_ConsoleOutput'].get_buffer()

    def arp_window_init(self):
        builder = Gtk.Builder()
        builder.add_from_file("GUI/ARP_Settings.glade")
        builder.connect_signals(self)

        self.arp_window = builder.get_object("window1")
        self.arp_window.set_transient_for(self.mainWindow)

        self.arp_buttons = {}
        self.add_controls(builder, self.arp_buttons, Control.arp_buttons)

        self.arp_entry = {}
        self.add_controls(builder, self.arp_entry, Control.arp_entry)

    @staticmethod
    def add_controls(builder, dict, ctl_list):
        """Method used to dynamically load all controls from the lists in Controls.py"""
        for controlstr in ctl_list:
            value = builder.get_object(controlstr)

            if value is None:
                print("Warning: {} is None!".format(controlstr))

            dict[controlstr] = value

    def onStop_Clicked(self, button):
        """Runs when the stop button is clicked"""
        self.progressRunning(False)
        self.clean_close()

    def onDeleteWindow(self, *args):
        """Event that runs when the window is closed"""

        if self.running:
            self.clean_close()

        Gtk.main_quit(*args)

    def latency_Clicked(self, button):
        """Event that runs when the latency button is clicked"""

        value = self.textBoxes['TextBox_Latency'].get_text()

        # Checks if the value is a valid int a checks for it's range
        if self.validation(value, 1, 1000):
            self.run_packet_capture('{} {}'.format(Parameter.cmd_latency, str(value)))

    def packet_loss_Clicked(self, button):
        """Event that runs when the packet loss button is clicked"""

        value = self.textBoxes['TextBox_PacketLoss'].get_text()

        # Checks if it is a valid int and if its within a specified range
        if self.validation(value, 1, 100):
            self.run_packet_capture('{} {}'.format(Parameter.cmd_packetloss, str(value)))

    def throttle_Clicked(self, button):

        value = self.textBoxes['TextBox_Throttle'].get_text()

        if self.validation(value, 1, 10000):
            self.run_packet_capture('{} {}'.format(Parameter.cmd_throttle, str(value)))

    def ratelimit_Clicked(self, button):
        value = self.textBoxes['TextBox_RateLimit'].get_text()

        if self.validation(value, 1, 10000):
            self.run_packet_capture('{} {}'.format(Parameter.cmd_ratelimit, str(value)))

    def simulate_Clicked(self, button):
        value = self.textBoxes['TextBox_Simulate'].get_text()

        print(value)
        if self.validation_str(Connection.connections, str(value)):
            self.run_packet_capture('{} {}'.format(Parameter.cmd_simulate, str(value)))
        else:
            print('Error: Cannot find simulation profile \'{}\''.format(value))

    def combination_Clicked(self, button):
        # TODO: Add functionality
        print('Combination!')

    def bandwidth_Clicked(self, button):
        self.run_packet_capture(Parameter.cmd_bandwidth)

    def outoforder_Clicked(self, button):
        self.run_packet_capture(Parameter.cmd_outoforder)

    def print_Clicked(self, button):
        self.run_packet_capture(Parameter.cmd_print)

    def graph_Clicked(self, button):
        self.clear_textView()

    # NEW BUTTONS HERE <-------------------------------------

    def ARP_Clicked(self, button):
        self.arp_window.show_all()

    def ARP_OK_Clicked(self, button):
        arp_valuesList = []
        arp_valuesList.append(self.arp_entry['TextBox_Interface'].get_text())
        arp_valuesList.append(self.arp_entry['Combo_Box_VictimIP'].get_active_text())
        arp_valuesList.append(self.arp_entry['Combo_Box_RouterIP'].get_active_text())

        # Clears the boxes
        self.arp_entry['TextBox_Interface'].set_text("")

        # Changing ID
        self.arp_window.hide()

        # Sets the stop button to on
        self.buttons['Button_stop'].set_sensitive(True)

        # Starts running the ARP Spoof
        parameters = "-i {0} -t {1} -r {2}".format(arp_valuesList[0], arp_valuesList[1], arp_valuesList[2])
        self.run_arp_spoof(parameters)

    def ARP_Cancel_Clicked(self, button):
        # Goes through and resets any text boxes
        self.arp_entry['TextBox_Interface'].set_text('')
        self.arp_window.hide()

    def onPacketFilter_Checked(self, checkBox):
        self.comboBox_packetFilter.set_sensitive(checkBox.get_active())

    def getLocalHosts_Clicked(self, button):
        active = scan_for_active_hosts()
        self.arp_entry['LevelBar_GetLocalHosts'].set_value(1)

        # Sets the values for the combo boxes
        for x in active:
            self.arp_entry['Combo_Box_VictimIP'].append_text(x)
            self.arp_entry['Combo_Box_VictimIP'].set_active(0)
            self.arp_entry['Combo_Box_RouterIP'].append_text(x)
            self.arp_entry['Combo_Box_RouterIP'].set_active(1)

    def run_packet_capture(self, parameters):
        """This method is used to run the Packet.py script"""

        # Toggles the buttons
        self.progressRunning(True)

        parameter_list = parameters.split(' ')

        # If the filter packet is toggled
        if self.checkBox_packetFilter.get_active():
            index = self.comboBox_packetFilter.get_active()
            model = self.comboBox_packetFilter.get_model()

            # Grab the selected item
            item = model[index]

            # Adds the selected item
            parameter_list.append(Parameter.cmd_target_packet + item[0])

        # The exact location of the file needs to specified

        # Command parameters
        cmd = ['pkexec', 'python', filepath + '/Packet.py']
        cmd = cmd + parameter_list

        # Calls the sub procedure
        self.packet_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        self.packet_outp = ""

        buffer = self.textViews['TextView_ConsoleOutput'].get_buffer()
        self.mark = buffer.create_mark('', buffer.get_end_iter(), True)

        # Non-Block updates the TextView
        GObject.timeout_add(100, self.update_terminal, self.textViews['TextView_ConsoleOutput'], self.packet_proc)

    def run_arp_spoof(self, parameters):
        """Runs the spoofing when called"""

        # Runs the arp spoofing
        cmd = ['pkexec', 'python', filepath + '/ArpSpoofing.py']
        cmd = cmd + parameters.split()  # Splits the parameter string into a list

        # Calls the sub procedure
        self.arp_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        self.arp_outp = ""

        # Non-Block updates the TextView
        GObject.timeout_add(100, self.update_terminal, self.textViews['TextView_ArpOutput'], self.arp_proc)

    @staticmethod
    def validation(string, start, stop):
        """This function is used to validate the passed parameter values
            it checks if the value can be parsed as an int and a range is
            specified that is must be within"""

        try:
            # Parsing
            integer = int(string)

            # Checks for the validation range
            if start <= integer <= stop:
                return True
            else:
                print('Error: Value needs to be between {} and {}'.format(start, stop))
                return False
        except ValueError:
            print('Error: Entered value is not an integer!')
            return False

    @staticmethod
    def validation_str(list, value):
        """Checks if the value is in the valid set"""

        for connection_type in Connection.connections:

            # If the value is in the list
            if value == connection_type.name:
                return True

        # Can't find value in lis
        return False

    @staticmethod
    def overwrite_line(buffer, text, mark):
        start = buffer.get_iter_at_mark(mark)
        buffer.insert(start, text)
        end = buffer.get_end_iter()
        buffer.delete(start, end)

    def update_terminal(self, TextView, sub_proc):
        """Used to pipe terminal output to a TextView"""

        buffer = TextView.get_buffer()

        # Grabs the console output
        bytes = self.non_block_read(sub_proc.stdout)

        if bytes is not None:
            value = bytes.decode()

            if b"\r" in bytes:
                # Grabs the most recent value with a \r
                parts = bytes.split(b'\r')
                value = parts[len(parts) - 2].decode()

                # Performs the action a \r would perform
                self.overwrite_line(buffer, value, self.mark)
            else:
                end = buffer.get_end_iter()
                # Display the output of the console
                buffer.insert(end, value)

                self.mark = buffer.create_mark('', end, True)

                # Keeps the most recent line on screen
                TextView.scroll_mark_onscreen(self.mark)

        return sub_proc.poll() is None

    @staticmethod
    def non_block_read(output):
        """Code for this was taken from @torfbolt answer on:
        https://stackoverflow.com/questions/17038063/show-terminal-output-in-a-gui-window-using-python-gtk
        """
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read()
        except:
            return ''

    def clean_close(self):
        """Function that is designed to stop the subprocess as cleanly as possible"""

        try:

            # Checks if the variables have been assigned and therefore if the process are running
            packet = False
            arp = False
            if hasattr(self, 'packet_proc'):
                if self.packet_proc is not None:
                    packet = True

            if hasattr(self, 'arp_proc'):
                if self.arp_proc is not None:
                    arp = True

            # Kill needs to be run from root because the sub process is launched from sudo
            # Runs the command together
            if packet and arp:
                os.system('pkexec kill -SIGINT ' + str(self.packet_proc.pid) + ' ' + str(self.arp_proc.pid))
                self.packet_proc.kill()
                self.arp_proc.kill()
            # Just kills the packet proc
            elif packet:
                os.system('pkexec kill -SIGINT ' + str(self.packet_proc.pid))
                self.packet_proc.kill()
            # Just kill the arp proc
            elif arp:
                os.system('pkexec kill -SIGINT ' + str(self.arp_proc.pid))
                self.arp_proc.kill()

        except Exception as e:
            print('Error in clean_close: ', e)

    def progressRunning(self, state):
        """Used to toggle the button being enabled, so when a progress is running
        the process buttons should be off and the cancel button enabled and visa versa"""

        # Keeps track of value
        self.running = state

        # Sets the latency and packet loss buttons sensitivity
        for button in self.buttons:
            self.buttons[button].set_sensitive(not state)

        # Inverts the stop button
        self.buttons['Button_stop'].set_sensitive(True)

        if state is False:
            # Clears all boxes
            for textbox in self.textBoxes:
                self.textBoxes[textbox].set_text('')

