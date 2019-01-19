# Setup.py
from setuptools import setup
from setuptools import find_packages

short_description = 'A tool designed to stress test a network to identify points of weakness'

long_description = ''' 
This project is a network simulation and network degradation simulator that has been designed
to be run a small computer emulating a router that will be the central point of the demonstration.
It's intended use is to incur hostile conditions on a network to stress aspects of a network
and determine it's breaking point. The tool can increase packet latency and packet loss, while also
being able to dynamically position it's self between a victim and a host by ARP Spoofing.
'''

classifiers = [
    # http://pypi.python.org/pypi?:action=list_classifiers
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: System Administrators'
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
    'Topic :: System :: Systems Administration'
    'Topic :: System :: Networking'
]

setup(name="DPS",
      version=1,
      description=short_description,
      install_requires=['NetfilterQueue', 'scapy', 'python-nmap', 'keyboard', 'matplotlib'],
      long_description=long_description,
      author="Aidan Fray",
      author_email="afray@hotmail.co.uk",
      url="",
      license='MIT',
      classifiers=classifiers,
      keywords='network degradation tool',
      packages=find_packages(),
      platforms=['LINUX']
)
