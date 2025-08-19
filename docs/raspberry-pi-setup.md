# Raspberry Pi USB/IP Seneye Bridge Setup

These steps set up your Raspberry Pi Zero 2W as a **USB/IP bridge** to expose the Seneye device to Home Assistant.

## 1. Flash Pi with Raspberry Pi OS Lite (64-bit)
Use Raspberry Pi Imager → choose "Lite (64-bit)".

Enable SSH, set hostname `seneye-pi`.

## 2. Install dependencies
```bash
sudo apt update
sudo apt install -y usbip jq git python3-pip
```

## 3. Clone Seneye USB Driver
```bash
git clone https://github.com/seneye/SUDDriver ~/SUDDriver
cd ~/SUDDriver/Cpp
make
```

## 4. Enable USB/IP
```bash
sudo modprobe usbip_core
sudo modprobe usbip_host
sudo usbipd -D
```

## 5. Share the Seneye USB device
```bash
usbip list -l
sudo usbip bind -b <busid>   # replace with your Seneye busid
```

## 6. Connect from Home Assistant host
On HA machine:
```bash
sudo apt install -y usbip
usbip attach -r seneye-pi.local -b <busid>
```

## 7. Verify
Seneye will appear under `/dev/usb/...`. The custom component polls it via `pyseneye`.

---
See repo README for HA config.
