#!/usr/bin/env bash
# scripts/install_dashboards.sh
# Copies Seneye dashboard YAMLs into Home Assistant's /config/dashboards/seneye
# and copies Blueprints into /config/blueprints/automation/seneye.
# Usage: bash scripts/install_dashboards.sh
set -euo pipefail

CONF_DIR="/config"
DASH_DST="$CONF_DIR/dashboards/seneye"
BP_DST="$CONF_DIR/blueprints/automation/seneye"

mkdir -p "$DASH_DST" "$BP_DST"

# Copy dashboards
cp -fv dashboards/seneye-dashboard.yaml "$DASH_DST/"
cp -fv dashboards/seneye-dashboard-apexcharts.yaml "$DASH_DST/" || true
cp -fv dashboards/seneye-dashboard-mushroom.yaml "$DASH_DST/" || true

# Copy blueprints
cp -fv blueprints/automation/seneye/seneye_nh3_high_alert.yaml "$BP_DST/"
cp -fv blueprints/automation/seneye/seneye_data_stale.yaml "$BP_DST/"
cp -fv blueprints/automation/seneye/seneye_ph_out_of_range.yaml "$BP_DST/" || true

echo
echo "✅ Copied dashboards to: $DASH_DST"
echo "✅ Copied blueprints to: $BP_DST"
echo
echo "Next steps:"
echo "1) Dashboards → Settings > Dashboards > Add Dashboard > YAML mode, then select one of:"
echo "   - $DASH_DST/seneye-dashboard.yaml (built-in)"
echo "   - $DASH_DST/seneye-dashboard-apexcharts.yaml (requires HACS apexcharts-card)"
echo "   - $DASH_DST/seneye-dashboard-mushroom.yaml (requires HACS Mushroom)"
echo "2) Blueprints → Settings > Automations & Scenes > Blueprints: 'Import Blueprint' → Upload files from $BP_DST"
echo
echo "Tip: If using ApexCharts or Mushroom, ensure their resources are added under Settings > Dashboards > Resources."
