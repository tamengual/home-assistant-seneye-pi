# Attaching Seneye from Home Assistant host (USB/IP client)

On the HA host (or the host OS running HA):
```bash
sudo apt update
sudo apt install -y linux-tools-$(uname -r) usbip
sudo modprobe vhci-hcd
usbip list -r <PI_HOST>
sudo usbip attach -r <PI_HOST> -b <BUSID>
usbip port
# A new /dev/hidraw* should appear
```
Make it persistent with a small systemd unit that runs `usbip attach` at boot.
