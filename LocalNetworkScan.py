import nmap
import socket


def scan_for_active_hosts():
    print('[!] Grabbing active hosts on your network')

    def grab_internal_ip():
        """This works by connecting with Google's DNS and grabbing the connection IP"""

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except ConnectionError:
            print("[!] Error: Cannot connect")

        # Takes of the last octive
        ip = '.'.join(ip.split('.')[:3])

        return ip

    try:
        nm = nmap.PortScanner()
        ip_range = grab_internal_ip() + '.1-255'
        nm.scan(hosts=ip_range, arguments='-sP')

        active_hosts = []
        for x in nm.all_hosts():
            # Saves all the active hosts
            if nm[x].state() == 'up':
                active_hosts.append(x)

        # So the script can be used two ways
        if __name__ == '__main__':
            print(active_hosts)
        else:
            return active_hosts

    except KeyboardInterrupt:
        print('[!] Local scan canceled')
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    scan_for_active_hosts()
