import unittest
import subprocess
import signal
import os

class Test(unittest.TestCase):

    def setUp(self):

        if os.geteuid() != 0:
            print("Please run as root!")
            exit()

    def test_print(self):

        cmd = "sudo python Parcel.py -p"

        with subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid) as process:
            try:
                output = process.communicate(timeout=5)[0]
            except subprocess.TimeoutExpired:
                process.send_signal(signal.SIGINT)


if __name__ == '__main__':
    unittest.main()