# wifi_deauth_multiple

## Prerequisites:
* root;
* WiFi adapter and drivers with Monitor mode support (better use dual-band adapter to cover 2.4 and 5 GHz networks);
* python3, python3-pandas, aircrack-ng, wireless-tools.
```
sudo apt update && apt upgrade
sudo apt install python3 python3-pandas python-is-python3 aircrack-ng wireless-tools
```

## Usage:
1. Start script;
```
python deauth.py
```
2. Select interface to be switched in Monitor mode;
3. Select interface in Monitor mode to be used for deauth (may have the same name as previous option);
4. __scan__, wait for target networks to appear (networks with bigger activity have more Packets);
5. Press __CTRL+C__;
6. __run__;
7. Type indexes of networks from p.4 separated with spaces (ex. "0", "0 1", "0 1 2");
8. To finish deauth press __CTRL+C__.

## Long run
Use __tmux__ session to keep script running after closing session:

* Start new session and then start script. When deauth started feel free to close window.
```
tmux new -s wifi
```
* Open previously started session
```
tmux attach
```

## System tweaks (for OPI Zero and others):

Assume __wlan1__ would be used in Monitor Mode

```
# do not rename new interfaces (ex. wlan1 to wlx*)
cat "extraargs=net.ifnames=0" >> /boot/armbianEnv.txt

# do not manage wlan1 with NetworkManager
cat "[keyfile]\nunmanaged-devices=interface-name:wlan1" >> /etc/NetworkManager/NetworkManager.conf

# disable powersave for managed wlan's
cat "[connection]\nwifi.powersave = 2" > /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf
```
Add to rc.local before exit
```
echo "cpu" > /sys/class/leds/orangepi:red:status/trigger # blink red led for cpu activity
```

