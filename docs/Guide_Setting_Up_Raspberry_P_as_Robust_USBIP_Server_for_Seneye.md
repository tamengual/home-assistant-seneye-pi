Got it — I’ve merged your troubleshooting steps into the existing GitHub-style documentation so the guide is now more complete and covers the issues you hit with `usbipd`, binding, and network errors. Here’s the **updated doc** you can drop into your repo or wiki:

---

# Guide: Setting Up a Raspberry Pi as a Robust USB/IP Server for Seneye

## Introduction

This guide details the process for configuring a Raspberry Pi to act as a reliable, auto-starting USB/IP server. This allows a USB device, such as a Seneye aquarium monitor, to be connected to the Pi and accessed over the network by a client, like the Home Assistant USB/IP Client add-on.

This setup is specifically designed to be resilient to reboots and to handle the power requirements of USB devices, which can be a common point of failure on Raspberry Pis.

---

## Required Hardware

For maximum stability, the following hardware is required:

1. **Raspberry Pi:** Any model with network connectivity. A Pi 4B is strongly recommended; a Pi Zero 2 W can work but is less reliable with USB power.
2. **High-Quality Power Supply:** An official or well-regarded supply (e.g., 5V 3A).
3. **Powered USB Hub:** Critical. Must have its own power adapter.
4. **SD Card:** 16 GB or larger, quality brand.
5. **Seneye Device.**

---

## Step 1: Flashing the Operating System

Follow the clean flash procedure with Raspberry Pi Imager → Raspberry Pi OS Lite (64-bit).
In Advanced Options, enable SSH, set user/password, configure Wi-Fi if needed, and **select the correct keyboard layout**.

---

## Step 2: Hardware Assembly

1. Insert the SD card.
2. Plug in powered hub → Pi.
3. Plug Seneye into powered hub.
4. Finally power the Pi.

---

## Step 3: Initial Software Configuration

1. SSH into the Pi.
2. Update and install usbip tools:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y usbip
   ```

   > Note: On Raspberry Pi OS Bookworm you may see errors if you try to install `linux-tools-$(uname -r)`. That’s expected — just install `usbip`, it already includes what you need.
3. Verify detection:

   ```bash
   lsusb
   ```

---

## Step 4: USB/IP Server Setup

### 4.1 Start usbipd

On Pi OS, the daemon is available at `/usr/sbin/usbipd`.

```bash
sudo nano /etc/systemd/system/usbipd.service
```

Paste:

```ini
[Unit]
Description=usbip host daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/usbipd -D
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now usbipd.service
```

Verify:

```bash
sudo systemctl status usbipd
sudo ss -tlnp | grep 3240
```

You should see `LISTEN` on port 3240.

---

### 4.2 Binding the Device

List devices:

```bash
sudo usbip list -l
```

Find the Seneye busid (e.g., `1-1`).

Bind it:

```bash
sudo usbip bind -b 1-1
```

If you get **“unable to bind”**, first unbind it from the HID driver:

```bash
echo -n '1-1:1.0' | sudo tee /sys/bus/usb/drivers/usbhid/unbind
sudo usbip bind -b 1-1
```

Success message: `bind device on 1-1: complete`.

---

### 4.3 Networking Notes

* `usbipd` listens on **all interfaces (0.0.0.0:3240)** by default.
* If your Pi can’t be reached:

  * Ensure the Pi has a fixed IP.
  * Verify you can `ping` it from HA.
  * Firewalls: Pi OS doesn’t use UFW by default. If you install ufw, allow port:

    ```bash
    sudo ufw allow 3240/tcp
    ```
* From HA, test:

  ```bash
  usbip list -r <pi-ip>
  ```

---

## Step 5: Automation

### 5.1 Load Kernel Module

```bash
echo 'vhci-hcd' | sudo tee -a /etc/modules
```

### 5.2 Auto-Bind on Boot

Edit root crontab:

```bash
sudo crontab -e
```

Add:

```cron
@reboot sleep 20 && /usr/sbin/usbip bind -b 1-1
```

This ensures rebind after reboot.

---

## Step 6: Safe Connect/Disconnect Workflow

### Disconnect (before reboot/power-off)

1. Stop HA USB/IP client add-on.
2. SSH to Pi:

   ```bash
   sudo usbip unbind -b 1-1
   ```
3. Then unplug Seneye or reboot Pi.

### Reconnect

1. Boot Pi fully.
2. Plug in Seneye.
3. Re-bind:

   ```bash
   sudo usbip bind -b 1-1
   ```
4. Start HA USB/IP client.

---

## Step 7: Troubleshooting Checklist

* **Device not showing in `lsusb`:**

  * Check powered hub.
  * Try direct Pi port (on Pi 4B use USB 2.0 ports, not 3.0).
* **`usbip: error: tcp connect`:**

  * Confirm `usbipd` is running.
  * Check `ss -tlnp` shows port 3240.
  * Confirm Pi’s IP is correct and reachable.
* **`unable to bind`:**

  * Use unbind from HID driver before binding.
* **Failed after reboot:**

  * Ensure `usbipd.service` is enabled.
  * Ensure crontab `@reboot` entry exists.
* **Power issues (mouse not lighting, Seneye dropouts):**

  * Replace hub with known-good powered hub.
  * Use Pi 4B instead of Pi Zero for more stable USB bus.

