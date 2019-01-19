import os


class Terminal:
    """This class is used statically to provide a central dynamic way to clear and print
    dynamically sized lines"""

    @staticmethod
    def clear_line():
        """Prints a dynamic line that is used to clear any left over fragments from previous prints"""

        h, w = Terminal.get_terminal_size()
        print('\r', ' ' * (w - 1), end='\r', flush=True)

    @staticmethod
    def print_sequence(seq, start='', end=''):
        """Used to print a dynamically sized sequence to the terminal"""

        h, w = Terminal.get_terminal_size()

        seq_len = len(seq)

        if seq_len > w:
            raise Exception('Error: Sequence is larger than the terminal width')
        else:
            # Re adjusts the sizings
            w -= len(start) + len(end) + 1

            times_to_print = round(w / seq_len)

            print(start, end='')
            print(seq * times_to_print, end='')
            print(end)

    @staticmethod
    def get_terminal_size():
        """gets the height and width of the current terminal"""

        terminal_height, terminal_width = os.popen('stty size', 'r').read().split()

        # Parses to ints and adds a buffer
        return int(terminal_height), int(terminal_width)
