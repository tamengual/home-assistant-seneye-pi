# Home Assistant Seneye Integration (Pi Bridge Edition)

This is a custom integration to connect your **Seneye Reef / Pond / Home** device to Home Assistant.

It uses a Raspberry Pi as a **USB/IP bridge**, following the setup instructions in [`docs/raspberry-pi-setup.md`](docs/raspberry-pi-setup.md).

## Installation

### HACS (preferred)
1. Go to HACS → Integrations → Custom repositories
2. Add this repo: `https://github.com/tamengual/home-assistant-seneye-pi`
3. Search for **Seneye** and install

### Manual
Copy `custom_components/seneye` into your Home Assistant `custom_components` folder.

## Setup
After install, restart Home Assistant. Then add the Seneye integration from the UI.

---
Maintained by @tamengual
