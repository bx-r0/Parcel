<img align="right" src="./parcel.png" width=175></img>
# Parcel
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

## Demonstration <a href="https://asciinema.org/a/HBbyLMCF6LjJF9dZE2hZspz4y" target="_blank"><img src="https://asciinema.org/a/HBbyLMCF6LjJF9dZE2hZspz4y.svg"/></a>

## Install - Debian or Ubuntu

```
sudo apt-get install build-essential python-dev libnetfilter-queue-dev
sudo python Setup.py install
```

## Install - Arch

Install ```aur/python-netfilterqueue-git``` https://aur.archlinux.org/packages/python-netfilterqueue-git/

```sudo python Setup.py install```


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
## ---- Effects:

--print, -p                                  
    * Prints all the packets
    
--ignore, -i
    * Does nothing to the packets. Used to show how much overhead there
    by default
    
--display-bandwidth, -b                     
    * Displays information on the transfer rate
      
--latency, -l <delay_ms>            
    * Applies latency on the connection   
    
--packet-loss, -pl  <loss_percentage>  
    * Performs packet loss on the connection

--surge, -t      <delay_ms> 
    * Creates a packet surge on a connection by the given delay 

--rate-limit, -rl   <rate_bytes>            
    * Limits the throughput of the program
    
## ---- Extra Optionals:

--target-packet, -tp    <packet-type>        
    * Only performs an effect on the specified packet type

--save, -s              <filename>
    * Tells the program to start saving all the packets that run through the system
    
```
