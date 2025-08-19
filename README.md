# Seneye USB Sensor — Home Assistant Custom Integration

Local‑first integration for **Seneye USB** probes. Polls the device via `pyseneye` and exposes sensors for Temperature, pH, NH3, PAR, PUR, LUX, Kelvin; plus binary sensors for **In Water** and **Slide Problem**. Includes UI options (poll interval + calibration), diagnostics export, and a `seneye.force_update` service.

**Repo:** https://github.com/tamengual/home-assistant-seneye-pi

## Install via HACS (Custom Repository)
1. HACS → … → **Custom repositories** → Add `https://github.com/tamengual/home-assistant-seneye-pi` (type: Integration)
2. Install **Seneye USB Sensor**
3. Restart Home Assistant
4. Settings → Devices & Services → **Add Integration** → *Seneye USB Sensor*

## USB/IP Pi Bridge
See `docs/raspberry-pi-usbip.md` and `docs/home-assistant-attach.md` to run the Seneye on a Raspberry Pi near the tank and attach it to your HA host over USB/IP.

## Trouble?
- If dependency installation fails, use an unpinned requirement (`"pyseneye"`) in `manifest.json`.
- If legacy template entities collide, rename/remove them to avoid duplicate IDs.
