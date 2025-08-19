# Raspberry Pi USBIP Bridge for Seneye

Use a Raspberry Pi to export the Seneye USB over **USB/IP**, then attach it from your HA host.

## Pi setup
```bash
sudo apt update
sudo apt install -y linux-tools-$(uname -r) usbip hwdata
echo -e "usbip-host
vhci-hcd" | sudo tee /etc/modules-load.d/usbip.conf
sudo modprobe usbip-host
sudo systemctl enable --now usbipd
```

## Bind the Seneye
```bash
usbip list -l            # find busid (e.g. 1-1.3)
sudo usbip bind -b 1-1.3
```

To auto-bind by VID:PID, see the service example in comments of this doc.
