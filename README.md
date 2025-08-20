# Home Assistant – Seneye (HID / USB‑IP / MQTT)

Universal Seneye integration for Home Assistant. Works with direct USB, a Raspberry Pi USB/IP bridge, or an optional MQTT publisher.
Shipped with **dashboards**, **blueprints**, and **automations** for an instant, useful setup.

> **Honesty check:** Confirmed working on **Direct USB** and **Raspberry Pi USB/IP** (our current live setup).  
> **Expected to work** (not yet fully verified): AquaPi MQTT bridge, Windows USB/IP, network USB hubs, and other Linux bridges—likely with minor tinkering. PRs welcome!

---

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Which setup should I choose?](#which-setup-should-i-choose)
- [Install the integration (HACS or manual)](#install-the-integration-hacs-or-manual)
- [Setup A – Direct USB (HID backend)](#setup-a--direct-usb-hid-backend)
- [Setup B – Raspberry Pi as USB/IP bridge (confirmed)](#setup-b--raspberry-pi-as-usbip-bridge-confirmed)
- [Setup C – MQTT publisher (Pi / AquaPi / Linux / Windows)](#setup-c--mqtt-publisher-pi--aquapi--linux--windows)
- [Setup D – Windows USB/IP server (untested, expected to work)](#setup-d--windows-usbip-server-untested-expected-to-work)
- [Setup E – Network USB hubs (guidance)](#setup-e--network-usb-hubs-guidance)
- [Options & Services](#options--services)
- [Dashboards, Blueprints & Automations](#dashboards-blueprints--automations)
- [Troubleshooting](#troubleshooting)
- [Tested & Untested Setups](#tested--untested-setups)
- [Contributing](#contributing)
- [License](#license)

---

## Features

* **Multiple Backends**: Connect via the method that best suits your setup.
    * **HID (Default)**: For devices directly connected via USB or attached over the network using a USB/IP client.
    * **MQTT**: For devices connected to a remote computer (like a Raspberry Pi or AquaPi), which then publishes sensor data over the network.
* **Standalone MQTT Publisher**: A lightweight Python script with a `systemd` service to run on any Linux-based machine (e.g., Raspberry Pi) that has the Seneye device attached.
* **Pre-made Dashboards**: Three ready-to-use Lovelace dashboards to visualize your Seneye data (Standard, ApexCharts, and Mushroom).
* **Automation Blueprints**: Easy-to-configure blueprints for critical alerts, including high NH3, pH out of range, and stale data warnings.
* **Installer Scripts**: Helper scripts for Linux and Windows to automate the installation of the dashboard files.

---

## Architecture

This diagram illustrates the different ways you can connect your Seneye device to Home Assistant using this integration.

```text
Seneye USB Probe
   |
   |--> [Option 1: Direct Connection]
   |      |
   |      +--> Home Assistant Host (using HID Backend)
   |
   |--> [Option 2: USB over Network]
   |      |
   |      +--> Raspberry Pi / PC (running USB/IP Server)
   |           |
   |           +-- (USB over IP) --> Home Assistant (using USB/IP Client & HID Backend)
   |
   +--> [Option 3: MQTT over Network]
          |
          +--> Any PC / Pi (running MQTT Publisher Script)
               |
               +-- (MQTT) --> MQTT Broker
                              |
                              +-- (MQTT) --> Home Assistant (using MQTT Backend)
```
- **HID** (default) reads `/dev/hidraw*` (works for direct USB *and* when HA attaches a USB/IP device).
- **MQTT** backend subscribes to `<prefix>/state` with parsed readings (publisher included here).

## Recommended Hardware for Raspberry Pi Setups

If you are connecting your Seneye to a Raspberry Pi (for either the USB/IP or MQTT methods), using the correct power hardware is critical for stability. Raspberry Pis can be sensitive to power demands, which can lead to USB devices not being detected after a reboot and potential SD card corruption.

To prevent these issues, the following hardware is strongly recommended:

High-Quality Power Supply: Use an official or well-regarded power supply for your specific Raspberry Pi model (e.g., 5V 3A for a Pi 4 or Zero 2 W). Do not use a standard phone charger.

Powered USB Hub: This is the most important component for reliability. A powered hub has its own power adapter and provides stable, consistent power to the Seneye probe, bypassing the Pi's own power limitations.

Correct Connection: Raspberry Pi → Powered USB Hub → Seneye Probe
---

## Which setup should I choose?

| Scenario | Recommended path | Notes |
|---|---|---|
| Seneye plugged into HA box | **Setup A: Direct USB (HID)** | Easiest |
| Seneye in another room; Pi nearby | **Setup B: Pi USB/IP (HID on HA)** | Confirmed working |
| Want to decouple transport or use AquaPi/PC | **Setup C: MQTT publisher** | Publisher included |
| Windows machine shares Seneye | **Setup D: USB/IP (usbipd-win)** | Expected to work |
| Network USB hub | **Setup E guidance** | Depends on hub |

---

## Install the integration (HACS or manual)

### Option 1 – HACS (recommended for updates)
1. In HA, install **HACS** (if not already).
2. HACS → **Integrations** → **Custom repositories** → add your repo URL under *Integration*.
3. Search **Seneye** → **Install**.
4. Restart HA. Then **Settings → Devices & Services → Add Integration → Seneye**.

### Option 2 – Manual copy
1. Copy `custom_components/seneye/` into your HA `/config/custom_components/`.
2. Restart HA.
3. **Settings → Devices & Services → Add Integration → Seneye**.

> After adding, open the **integration options** to confirm **Backend** (defaults to HID).

---

## Setup A – Direct USB (HID backend)

No extra host setup needed if HA can see `/dev/hidraw*`.

1. Plug Seneye into the HA host (or the VM/host that passes through hidraw).
2. Add the **Seneye** integration.
3. In options, keep **Backend = HID**.
4. Call **`seneye.connection_test`** (Developer Tools → Services). You should see a success message.

**Tip:** If permissions block access to hidraw on some distros, ensure the HA user/container has access to `/dev/hidraw*` and relevant udev rules.

---

## Setup B – Raspberry Pi as USB/IP bridge (confirmed)

We use a Pi as a **USB/IP server** so HA “attaches” the Seneye as if local. The integration still uses **HID**.

### On the Raspberry Pi (server)
```bash
# Install tools
sudo apt update
sudo apt install -y usbip

# Load module now and on boot
sudo modprobe usbip_host

# Install helper script to bind the Seneye by VID:PID
sudo tee /usr/local/sbin/bind-seneye.sh >/dev/null <<'EOF'
#!/bin/bash
VENDOR_ID="24f7"
PRODUCT_ID="2204"
/usr/sbin/usbip unbind --busid=$(/usr/sbin/usbip list -p -l | grep "#usbid=${VENDOR_ID}:${PRODUCT_ID}" | cut -d'=' -f2 | cut -d'#' -f1) 2>/dev/null || true
sleep 2
/usr/sbin/usbip bind --busid=$(/usr/sbin/usbip list -p -l | grep "#usbid=${VENDOR_ID}:${PRODUCT_ID}" | cut -d'=' -f2 | cut -d'#' -f1)
EOF
sudo chmod +x /usr/local/sbin/bind-seneye.sh

# Systemd unit
sudo tee /etc/systemd/system/usbip-bind-seneye.service >/dev/null <<'EOF'
[Unit]
Description=USBIP Bind Seneye Device
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/bash /usr/local/sbin/bind-seneye.sh
RemainAfterExit=true
StandardOutput=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now usbip-bind-seneye
```

### On Home Assistant (client)
- Install a **USB/IP client** add-on (community) or configure the host OS to attach the device from the Pi’s IP.
- Once attached, HA should expose a `/dev/hidraw*`. Keep **Backend = HID** in Seneye options.
- Call **`seneye.connection_test`** to verify.

> This is our **current, confirmed working** topology.

---

## Setup C – MQTT publisher (Pi / AquaPi / Linux / Windows)

Use this if you want a simple network transport. The publisher reads the Seneye via `pyseneye` and publishes **one retained JSON** to `<prefix>/state`. The integration (MQTT backend) ingests that payload and creates the same entities.

### On the machine with Seneye plugged in
```bash
# Requirements
sudo apt update && sudo apt install -y python3-venv git
sudo mkdir -p /opt/seneye-mqtt && sudo chown $USER:$USER /opt/seneye-mqtt
cd /opt/seneye-mqtt

# Copy the publisher directory from this repo (mqtt_publisher/)
# e.g., scp or git clone then copy:
# cp -r ~/home-assistant-seneye-pi/mqtt_publisher ./

python3 -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r mqtt_publisher/requirements.txt

# Configure environment
sudo tee /etc/default/seneye-mqtt >/dev/null <<'EOF'
MQTT_HOST=192.168.1.10
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_PREFIX=seneye
INTERVAL=300
HIDRAW_PATH=
EOF

# Install systemd unit
sudo cp mqtt_publisher/systemd/seneye-mqtt.service /etc/systemd/system/seneye-mqtt.service
sudo systemctl daemon-reload
sudo systemctl enable --now seneye-mqtt
systemctl status seneye-mqtt --no-pager
```

**What you should see in MQTT**
- `seneye/status` → `online` (retained)  
- `seneye/state` → JSON payload like:
```json
{"temperature":25.1,"ph":8.15,"nh3":0.01,"par":150,"pur":60,"lux":12000,"kelvin":6500,"in_water":true,"slide_expired":false}
```

**Tip:** If auto-detection fails, set `HIDRAW_PATH` manually. Find it with:
```bash
ls -l /dev/hidraw*
```

### In Home Assistant
- Open Seneye **Options** → set **Backend = MQTT** and configure **MQTT prefix** (default `seneye`).
- Run **`seneye.connection_test`**.

> AquaPi & Windows as publishers are expected to work with the same script. On Windows, install Python, then run the script in a venv and set env vars; use Task Scheduler for autostart.

---

## Setup D – Windows USB/IP server (untested, expected to work)

Using **usbipd-win** to share the Seneye from a Windows PC:
```powershell
# As admin on Windows
winget install usbipd
usbipd wsl list   # or: usbipd list
usbipd bind --busid <BUSID>   # share the device
```

Then on the HA host, **attach** the shared device using a USB/IP client (add-on/host tooling). Once attached, you should see `/dev/hidraw*` and can use **HID** backend as usual.

> We haven’t run this end-to-end yet, but it follows the same pattern as the Pi USB/IP approach.

---

## Setup E – Network USB hubs (guidance)

Many network USB hubs implement USB/IP under the hood. If you can **attach** the device to the HA host so it appears as `/dev/hidraw*`, use **HID** backend. If the hub requires a companion PC, run the **MQTT publisher** on that PC and use **MQTT** backend.

---

## Options & Services

**Options (via Configure on the integration card):**
- **Backend**: `hid` (default) / `mqtt`
- **Update interval** (minutes)
- **Temperature offset** (°C), **pH offset**
- **PAR scale** (multiply PAR; useful if you calibrate externally)
- **MQTT prefix** (`seneye` by default)

**Services:**
- `seneye.force_update` – immediately poll the backend
- `seneye.connection_test` – quick end-to-end test with a UI notification

---

## Dashboards, Blueprints & Automations

We ship three dashboards and three blueprints + premade automations.

### Quick installers
**Terminal/SSH on HA:**
```bash
bash scripts/install_dashboards.sh
```
**Windows (SMB share):**
```powershell
.\scripts\Install-Dashboards.ps1 -ConfigShare \homeassistant\config
```

### Dashboards (YAML mode → pick file)
- `dashboards/seneye-dashboard.yaml` – built‑in cards only
- `dashboards/seneye-dashboard-apexcharts.yaml` – **requires HACS apexcharts-card**
- `dashboards/seneye-dashboard-mushroom.yaml` – **requires HACS Mushroom** (NH3 “danger dial”)

### Blueprints (UI → Automations & Scenes → Blueprints → Import → Upload)
- `blueprints/automation/seneye/seneye_nh3_high_alert.yaml`
- `blueprints/automation/seneye/seneye_ph_out_of_range.yaml`
- `blueprints/automation/seneye/seneye_data_stale.yaml`

### Premade automations
- `automations/seneye_automations.yaml` – copy/paste or merge into `automations.yaml`

---

## Troubleshooting

**No entities after adding integration**
- Check **Settings → System → Logs** for `custom_components.seneye` messages.
- Ensure the correct **Backend** is selected (HID for direct USB/USB‑IP; MQTT for publisher).

**HID device not found**
- Verify `/dev/hidraw*` exists on the HA host/container.
- For USB/IP: confirm client is attached; reattach after reboots if needed.
- Permissions/udev may be required on some host setups.

**MQTT shows offline or no state**
- `journalctl -u seneye-mqtt -f` (publisher logs)  
- Verify broker, username/password, and `MQTT_PREFIX` match integration options.
- Confirm the retained state at `<prefix>/state` and status at `<prefix>/status` in your MQTT explorer.

**pyseneye errors**
- The integration installs `pyseneye` automatically; for the publisher, run `pip install -r mqtt_publisher/requirements.txt`.

**Debug logging in HA**
```yaml
logger:
  default: warning
  logs:
    custom_components.seneye: debug
```

---

## Tested & Untested Setups

### Confirmed Working
- ✅ Home Assistant OS (Supervised, Core, Container)
- ✅ Raspberry Pi (Zero 2W / 4) **USB/IP bridge** → HA attaches device → **HID backend**
- ✅ Direct USB to HA host → **HID backend**

### Expected to Work (with minor tinkering)
- ⚠️ AquaPi (via MQTT publisher)
- ⚠️ Windows USB/IP (usbipd‑win)
- ⚠️ Network USB hubs; other Linux bridges

*It may be possible to modify AquaPi to behave like the Pi USB/IP bridge; unverified.*

### Call for testers
If you get one of the untested paths running, please open an **issue** or **PR** with details so we can add it to the confirmed list.

---

## Contributing

Issues and PRs are welcome:
- Bugfixes, new dashboards/blueprints, docs improvements
- Additional backends/bridges
- Test confirmations for the “Expected to work” setups

---

## License

MIT
