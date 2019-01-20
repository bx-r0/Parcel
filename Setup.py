# Setup.py
from setuptools import setup
from setuptools import find_packages

short_description = 'A tool designed to stress test a network to identify points of weakness'

long_description = short_description

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
      install_requires=['NetfilterQueue', 'scapy'],
      long_description=long_description,
      author="Aidan Fray",
      url="",
      license='MIT',
      classifiers=classifiers,
      keywords='network degradation tool',
      packages=find_packages(),
      platforms=['LINUX']
)
