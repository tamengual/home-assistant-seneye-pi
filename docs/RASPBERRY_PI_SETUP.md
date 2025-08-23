# Guide: Setting Up a Raspberry Pi as a Robust USB/IP Server for Seneye

## Introduction
This guide details the final, successful process for configuring a Raspberry Pi to act as a reliable, auto-starting USB/IP server. This allows a USB device, such as a Seneye aquarium monitor, to be connected to the Pi and accessed over the network by the Home Assistant USB/IP Client add-on.

This setup is specifically designed to be resilient to reboots and to handle the hardware incompatibilities and driver conflicts discovered during extensive testing.

## Required Hardware
For maximum stability, the following hardware is **required**:

1.  **Raspberry Pi:** A Raspberry Pi 4 Model B is recommended for best compatibility. The Pi Zero 2 W may have hardware/firmware incompatibilities with some USB hubs.
   a. A raspberry Pi zero 2W with this attachment has been tested and seems stable: https://www.amazon.com/dp/B06Y2TSR1D?ref=ppx_yo2ov_dt_b_fed_asin_title 
3.  **High-Quality Power Supply:** An official or well-regarded power supply for your specific Pi model.
4.  **Powered USB Hub:** This is **critical**. The hub must have its own dedicated power adapter.
5.  **SD Card:** A quality SD card, 16GB or larger.

---

## Step 1: Flash and Configure the OS

1.  Use the **Raspberry Pi Imager** to install a fresh copy of **Raspberry Pi OS Lite (64-bit)** onto your SD card.
2.  In the advanced settings, pre-configure your username, password, Wi-Fi, and **enable SSH**.

---

## Step 2: Assemble Hardware and Set Up Software

1.  Assemble the hardware as described in the main `README.md` (Pi -> Powered Hub -> Seneye).
2.  Boot the Pi, SSH in, and run a full system update and install the necessary `usbip` tools:
    ```bash
    sudo apt update && sudo apt upgrade -y && sudo apt install usbip -y
    ```
3.  Verify the Seneye is detected with `lsusb` and find its `busid` with `sudo usbip list -l`.

---

## Step 3: Automate the USB/IP Server

This is the final, robust automation that correctly handles startup timing and driver conflicts.

1.  **Set the Kernel Driver to Load on Boot:**
    ```bash
    echo 'vhci-hcd' | sudo tee -a /etc/modules
    ```

2.  **Create the USB/IP Daemon Service:**
    Create the file `sudo nano /etc/systemd/system/usbipd.service` and paste the following:
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
    Then, enable it:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable usbipd.service
    ```

3.  **Create the Automatic Bind Service:**
    This service waits for the daemon to start, waits an additional 10 seconds, attempts to detach the default driver, and then binds the Seneye.
    
    Create the file `sudo nano /etc/systemd/system/usbip-bind-seneye.service`. **Remember to replace `1-1.1`** with the correct bus ID for your device.
    ```ini
    [Unit]
    Description=USB/IP Bind Seneye Device
    After=usbipd.service
    Wants=usbipd.service

    [Service]
    Type=oneshot
    ExecStart=/bin/sh -c "sleep 10 && echo -n '1-1.1:1.0' > /sys/bus/usb/drivers/usbhid/unbind 2>/dev/null || true && /usr/sbin/usbip bind -b 1-1.1"

    [Install]
    WantedBy=multi-user.target
    ```
    Then, enable it:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable usbip-bind-seneye.service
    ```
4. **Reboot the Pi** (`sudo reboot`). After it restarts, the Seneye will be automatically shared and ready for Home Assistant.
EOF

# 3. Update the main README.md to point to the new guide
# Note: This command uses sed to find and replace a block of text in the README.
sed -i.bak '
/## Recommended Hardware for Raspberry Pi Setups/,/## Installation/ {
  /## Recommended Hardware for Raspberry Pi Setups/ {
    i\
\
---
    h
    s/.*/## Raspberry Pi Setup for USB\/IP or MQTT\
\
This integration can be used with a Raspberry Pi acting as a remote host for the Seneye probe. This is useful for placing the probe far from your Home Assistant server.\
\
Due to the complexities and potential hardware incompatibilities of setting up a robust USB\/IP server, a **detailed, step-by-step guide** has been created.\
\
➡️ **See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for complete instructions.**\
\
Following this guide is **highly recommended** for a stable, "set it and forget it" system.\
