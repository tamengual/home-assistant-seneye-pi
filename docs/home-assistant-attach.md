You are absolutely right. My apologies. We troubleshooted the files so much that I defaulted to the wrong set of instructions for the client setup. You are correct that we did not use SSH for the Home Assistant side, and the UI-based Add-on method is much simpler.

Let's get this documented correctly. Here are the detailed instructions for setting up the **USBIP Client Add-on** in Home Assistant to connect to your already-configured Pi server.

-----

## **Connecting the Seneye via the USBIP Add-on**

This guide assumes your Raspberry Pi server is already running and sharing the Seneye device. These steps are performed entirely within the Home Assistant user interface.

### **Step 1: Install the USBIP Client Add-on**

First, we need to find and install the community add-on that will act as our USBIP client.

1.  Navigate to **Settings \> Add-ons**.
2.  Click the blue **ADD-ON STORE** button in the bottom right.
3.  Search the store for `USBIP`. You should find an add-on named **"USBIP Client"** or something similar from the list of community add-ons.
4.  Click on the add-on and then click **INSTALL**. Wait for the installation to complete.

-----

### **Step 2: Configure the Add-on**

This is the most important step. We need to tell the add-on where your Raspberry Pi server is and which device to connect to.

1.  After installation, go to the **Configuration** tab of the USBIP Client add-on.

2.  The configuration will be in YAML format. You will need to provide the IP address of your Pi server and the Bus ID of the Seneye device you found earlier.

3.  Go to the configuration tab of the Add on. Click on the 3 dots in the top right to "edit in yaml" Modify the configuration to look like the example below, replacing the placeholder values with your actual information.

    ```yaml
    log_level: info
    discovery_server_address: ""
    devices:
      - server_address: 192.168.1.10
        bus_id: 1-1
    hosts: []

    ```

      * **server**: Replace `192.168.1.10` with the IP address of your Raspberry Pi.
      * **devices**: Under this section, list the Bus ID of your Seneye device. In the example, it's `1-1`. Yours may be different.

4.  Click **SAVE**.

-----

### **Step 3: Start the Add-on**

Now that the configuration is saved, you can start the service.

1.  Navigate to the **Info** tab of the add-on.
2.  Click **START**.
3.  For persistence, also enable the **"Start on boot"** toggle. This ensures the virtual USB connection is automatically re-established whenever you restart Home Assistant.

-----

### **Step 4: Verify and Troubleshoot**

You can immediately see if the connection was successful by checking the logs.

1.  Click the **Log** tab within the add-on.
2.  If the connection is successful, you will see messages like "device attached" or "new port created."
3.  If the connection fails, you might see errors like "connection refused" or "device not found." If this happens:
      * Double-check that the `server` IP address in the configuration is correct.
      * Confirm that the `devices` Bus ID matches the one from your Pi.
      * Ensure that the USBIP server is still running on your Raspberry Pi (`sudo usbipd -D`) and that the device is bound.
