# Parcel
Lightweight packet manipulation script build onto of the Linux NFQUEUE. Design to simulate common forms of network degradation.

It can simulate:

- Latency
- Packet loss
- Restricted bandwidth
- Out of order packets
- Packet surges

Alongside:

- Printing packets
- Display current bandwidth
- Saving to .pcap files

## Install - Debian or Ubuntu

```sudo apt-get install build-essential python-dev libnetfilter-queue-dev```
```sudo python Setup.py install```

## Install - Arch

Install ```aur/python-netfilterqueue-git``` https://aur.archlinux.org/packages/python-netfilterqueue-git/

```sudo python Setup.py install```


## Get started

Run ```sudo Parcel.py -h ``` for the usage

### Examples.
Command will print all packets flowing in and out of the current machine
```sudo python Parcel.py -p```

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
    * Creates a packet surge on connection by the given delay 

--rate-limit, -rl   <rate_bytes>            
    * Limits the throughput of the program
    
--out-of-order, -o 
    * Sets the mode to out of order that alters the order of incoming packets
    
## ---- Extra Optionals:

--target-packet, -tp    <packet-type>        
    * Only performs an affect on the specified packet type

--save, -s              <filename>
    * Tells the program to start saving all the packets that run through the system
    
```