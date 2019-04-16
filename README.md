<img align="right" src="./parcel.png" width=175></img>
# Parcel

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bfce2c825f44424c969e888c3ebfc90a)](https://app.codacy.com/app/AidanFray/Parcel?utm_source=github.com&utm_medium=referral&utm_content=AidanFray/Parcel&utm_campaign=Badge_Grade_Dashboard)

Lightweight packet manipulation script built on top of the Linux NFQUEUE. Designed to simulate common forms of network degradation.

## Effects
- Latency
- Packet loss
- Restricted bandwidth
- Packet surges

## Extra features
- Printing packets
- Display current bandwidth
- Saving to .pcap files
- Filter by protocol

## Install - Debian or Ubuntu

```
sudo apt-get install build-essential python-dev libnetfilter-queue-dev
sudo pip install -r requirements.txt
```

## Install - Arch

Install ```aur/python-netfilterqueue-git``` https://aur.archlinux.org/packages/python-netfilterqueue-git/

```sudo pip install -r requirements.txt```


## Get started

Run ```sudo Parcel.py -h ``` for the usage

### Packet print
Command will print all packets flowing in and out of the current machine:

```sudo python Parcel.py -p```


### Filter TCP
To filter for certain packets for a certain protocol the ```-tp``` is used:

```sudo python Parcel.py -p -tp TCP```

# Usage

```
EFFECTS
Only one effect can be selected 

-p                      Prints all the packets
-i                      Does nothing to the packets. Used to show how much default overhead there is
-b                      Displays information on the transfer rate
-l    <delay_ms>        Applies latency on the connection   
-pl   <percentage>      Performs packet loss on the connection
-t    <delay_ms>        Creates a packet surge on a connection by the given delay 
-rl   <rate_bytes>      Limits the throughput of the program
    
OPTIONS 
Can be used with any effect

-tp   <packet-type>     Only performs an effect on the specified packet type
 -s   <filename>         Saves all collected packets into a .pcap file
```
