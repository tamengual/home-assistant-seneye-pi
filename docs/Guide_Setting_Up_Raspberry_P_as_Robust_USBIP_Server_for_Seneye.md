# Guide: Setting Up a Raspberry Pi as a Robust USB/IP Server for Seneye

## Introduction
This guide details the process for configuring a Raspberry Pi to act as a reliable, auto-starting USB/IP server. This allows a USB device, such as a Seneye aquarium monitor, to be connected to the Pi and accessed over the network by a client, like the Home Assistant USB/IP Client add-on.

This setup is specifically designed to be resilient to reboots and to handle the power requirements of USB devices, which can be a common point of failure on Raspberry Pis.

## Required Hardware
For maximum stability, the following hardware is required:

1.  **Raspberry Pi:** Any model with network connectivity (Ethernet or Wi-Fi).
2.  **High-Quality Power Supply:** An official or well-regarded power supply for your specific Pi model (e.g., 5V 3A).
3.  **Powered USB Hub:** This is critical. The hub must have its own dedicated power adapter to provide stable power to the USB device.
4.  **SD Card:** A quality SD card, 16GB or larger.
5.  **Seneye Device:** The USB device you intend to share.

---

## Step 1: Flashing the Operating System

We will start with a completely clean OS to ensure there is no file corruption.

1.  Download and install the **Raspberry Pi Imager** application on your main computer.
2.  Insert your SD card.
3.  In the Raspberry Pi Imager, select your Pi model and the **Raspberry Pi OS Lite (64-bit)**.
4.  Click the gear icon for "Advanced Options" and pre-configure the following:
    * **Enable SSH:** Check the box to allow remote access.
    * **Set username and password:** Create your user.
    * **Configure wireless LAN:** Enter your Wi-Fi credentials if you are not using an Ethernet cable.
    * make sure you select the correct keyboard during this step as an incorrect one will make it impossible to enter your password correctly
5.  Write the image to the SD card.

---

## Step 2: Hardware Assembly

1.  Ensure all components are unplugged from power.
2.  Insert the freshly flashed SD card into the Raspberry Pi.
3.  Plug the **powered USB hub** into a wall outlet.
4.  Connect the hub's data cable to a USB port on the Raspberry Pi.
5.  Connect the **Seneye device** to a port on the **powered hub**.
6.  Connect the **high-quality power supply** to the Raspberry Pi, then plug it into the wall to power it on.

---

## Step 3: Initial Software Configuration

1.  Wait a few minutes for the Pi to boot up for the first time.
2.  Find the Pi's IP address from your router's device list.
3.  SSH into the Raspberry Pi from your main computer (e.g., `ssh your_user@your_pi_ip_address`).
4.  Run a full system update and install the necessary `usbip` tools with this single command:
    ```bash
    sudo apt update && sudo apt upgrade -y && sudo apt install usbip -y
    ```
5.  Verify that the Seneye device is automatically detected. The powered hub should ensure this works correctly even after a reboot.
    ```bash
    lsusb
    ```
    You should see the "Seneye" device in the list of USB devices.

---

## Step 4: Automating the USB/IP Server

This is the core of the setup, ensuring all necessary components start automatically after a reboot.

1.  **Find the Bus ID:** Find the address of the Seneye device. You will need this for the automation script.
    ```bash
    sudo usbip list -l
    ```
    Note the `busid` (e.g., `1-1`).

2.  **Ensure Kernel Driver Loads on Boot:**
    ```bash
    echo 'vhci-hcd' | sudo tee -a /etc/modules
    ```

3.  **Create the USB/IP Daemon Service:**
    The `usbip` package does not always include a service file, so we will create one.
    
    a. Create and open the new service file:
    ```bash
    sudo nano /etc/systemd/system/usbipd.service
    ```
    b. Paste the following text into the editor:
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
    c. Save and exit the editor (`Control + O`, `Enter`, `Control + X`).

4.  **Enable the New Service:**
    Tell the system to load the new file and enable it to start on boot.
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable usbipd.service
    ```

5.  **Create the Automatic Bind Job:**
    This final step automatically runs the `bind` command shortly after boot, giving the system time to initialize properly.
    
    a. Open the system scheduler:
    ```bash
    sudo crontab -e
    ```
    b. If prompted, select `nano` as the editor.
    c. Add the following line to the bottom of the file. **Important:** Change `1-1` if the bus ID you found in Step 4.1 was different.
    ```cron
    @reboot sleep 20 && /usr/sbin/usbip bind -b 1-1
    ```
    d. Save and exit (`Control + O`, `Enter`, `Control + X`).

---

## Step 5: Final Test and Home Assistant Connection

You should wait to connect the Seneye until after the Pi has finished booting up. You should also disconnect it at the software level before you unplug it or reboot the Pi. This avoids the boot-up power issue and prevents potential file corruption.

5a. The Proper "Hot-Plug" Workflow

Here is the correct and safe sequence for connecting and disconnecting the Seneye to prevent errors.

To Safely Disconnect the Seneye (Before a Reboot) ⛔ : Before you unplug the USB cable or run sudo reboot, you need to safely "eject" it at the software level first.

1. Stop the Client: In Home Assistant, go to the USBIP Client add-on and click Stop. This tells HA to let go of the device.

2. Unbind the Device: SSH into your Raspberry Pi and run the following command to tell the Pi's server to release the device:

 ```bash
 sudo usbip unbind -b 1-1
```
3. Physically Unplug: It is now safe to unplug the Seneye's USB cable from the Pi. You can now safely run sudo shutdown now or sudo reboot.

5b. Reboot

1.  Reboot the Raspberry Pi to test the full automation.
    ```bash
    sudo reboot
    ```
2.  Wait about 30 seconds for the Pi to fully restart and for the startup task to run.
3.  In your Home Assistant interface, navigate to the **USBIP Client add-on**.
4.  In the add-on's configuration, ensure the `server_address` is the Pi's IP address and the `bus_id` matches the one you used in the `cron` job.
5.  Start the add-on. It should now connect successfully and remain stable.



5c. To Safely Connect the Seneye (After Booting) ✅
This is the reverse of the process, which is the temporary startup sequence we developed.

1. Wait for the Pi to fully boot up.

2. Physically Plug In: Connect the Seneye's USB cable to the Pi.

3. Bind the Device: SSH into the Pi and run the command to share the device:

   ```bash
   sudo usbip bind -b 1-1
   ```
4. Start the Client: Go to the USBIP Client add-on in Home Assistant and click Start.

Following this sequence will give you the most stable operation possible until your new powered USB hub arrives. The hub should eliminate the need for this entire process, as it will provide stable power from the very start of the boot sequence.

