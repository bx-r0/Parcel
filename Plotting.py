import os
import numpy as np
try:
    from matplotlib import animation
    from matplotlib import pyplot as plt
except ImportError:
    print('\nError: cannot import matplotlib, please install here')
    print('https://matplotlib.org/users/installing.html\n')
    exit(0)


# TODO: Put download link on README for matplotlib
class Graph:
    """This class is used to make a new graph
        Scatter Graph
            - add_points()
        Bar
            - increment_category()
        Line Graph
            - add_points()
    """

    def __init__(self):
        self.fig = plt.figure()
        self.x = []
        self.y = []
        self.n_index = 0
        self.barGraphLists = [[], []]  # Bar graph

        # Static
        self.file_number = 0
        self.picture_filename = 'Graphs/graph_0.png'
        self.colours = 'rgbkymc'  # Used for bar colours

    def refresh_filename(self):
        self.picture_filename = 'Graphs/graph_{}.png'.format(self.file_number)

    # TODO: Is it possible to dynamically find out who the user is?
    def show(self):
        """Used to display the graph using the 'feh' command"""

        self.save()

        # Shows the file
        os.system('sudo -u user_1 feh {}'.format(self.picture_filename))

    def save(self):
        """Saves the file to disk"""

        # Checks if there are existing files
        while os.path.isfile(self.picture_filename):
            self.file_number += 1
            self.refresh_filename()

        # Grabs the full filename
        filename = os.path.dirname(os.path.abspath(__file__))

        print(" " * 50, end='\r')  # Line clear
        print("[*] Your graph has been saved!", flush=True)
        print('[*] \t{}'.format(self.picture_filename), '\n[*]', flush=True)

        self.fig.savefig(self.picture_filename)

    def add_points(self, x, y):
        """Used to add values to the potential plot points"""
        self.x.append(x)
        self.y.append(y)

    def add_point(self, y):
        """Adds one point with an auto incrementing x"""
        self.x.append(self.n_index)
        self.n_index = self.n_index + 1
        self.y.append(y)

    def set_x_axis_label(self, label):
        """Sets the x axis for the most recent graph"""
        plt.xlabel(label)

    def set_y_axis_label(self, label):
        """Sets the y axis for the most recent graph"""
        plt.ylabel(label)

    def increment_catagory(self, name):
        """Used to keep track of values for a bar graph
        If the name doesn't exist, it's added to the list"""

        index = 0
        for n in self.barGraphLists[0]:

            # If the name is found, increment it's value
            if n == name:
                self.barGraphLists[1][index] += 1

                # Finish
                return

            index += 1

        # If the name isn't found
        self.barGraphLists[0].append(name)
        self.barGraphLists[1].append(1)

    def plot(self, colour='ro-'):
        """[Line Graph]"""
        """Adds all points to the graph, adds a line and displays the graph"""
        plt.plot(self.x, self.y, colour)
        self.show()

    def bar(self):
        """[Bar Graph]"""
        """Plots the bars for the graph"""

        x = np.arange(len(self.barGraphLists[0]))
        bar = plt.bar(x, self.barGraphLists[1])
        plt.xticks(x, self.barGraphLists[0])

        # Colour alternation
        total = 0
        for x in bar:

            # Reset when total goes over
            if total is len(self.colours):
                total = 0

            # Grabs a colour
            x.set_color(self.colours[total])
            total += 1

        self.show()

    def points(self, colour='ro-'):
        """[Scatter Graph]"""
        """Adds all the points to the graph (with no line) and display the graph"""

        for i in range(0, len(self.x)):
            plt.plot(self.x[i], self.y[i], colour)

        self.show()


class AnimateGraph:

    def __init__(self, limit_x, limit_y, custom_method=None):
        # Graph init
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, limit_x), ylim=(0, limit_y))
        self.line, = self.ax.plot([], [], lw=2)

        # Allows passing in of lambda functions
        self.graph_function = custom_method

        # Records
        self.limit_x = limit_x
        self.limit_y = limit_y

        # Data
        self.x = []
        self.y = []

    def init(self):
        """Called at the end and start of each interval"""
        return self.line,

    def set_x_axis_label(self, label):
        """Sets the x axis for the most recent graph"""
        plt.xlabel(label)

    def set_y_axis_label(self, label):
        """Sets the y axis for the most recent graph"""
        plt.ylabel(label)

    def animate(self, i):
        """The method that is called every frame"""

        if self.graph_function is not None:
            self.graph_function(i, self.x, self.y)

        self.line.set_data(self.x, self.y)
        return self.line,

    def add_points(self, x, y):
        self.x.append(x)
        self.y.append(y)

    def start(self):
        """Starts and displays the animated graph"""

        anim = animation.FuncAnimation(self.fig,
                                       self.animate,
                                       init_func=self.init,
                                       frames=2000,
                                       interval=20,
                                       blit=True)

        plt.show()