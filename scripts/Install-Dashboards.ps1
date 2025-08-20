
# scripts\Install-Dashboards.ps1
# Copies dashboards & blueprints to a Home Assistant config share.
# Usage (PowerShell): .\scripts\Install-Dashboards.ps1 -ConfigShare \\homeassistant\config
param(
  [string]$ConfigShare="\\homeassistant\config"
)

$DashDst = Join-Path $ConfigShare "dashboards\seneye"
$BpDst = Join-Path $ConfigShare "blueprints\automation\seneye"

New-Item -ItemType Directory -Force -Path $DashDst | Out-Null
New-Item -ItemType Directory -Force -Path $BpDst | Out-Null

Copy-Item -Force -Path "dashboards\seneye-dashboard.yaml" -Destination $DashDst
if (Test-Path "dashboards\seneye-dashboard-apexcharts.yaml") {
  Copy-Item -Force -Path "dashboards\seneye-dashboard-apexcharts.yaml" -Destination $DashDst
}
if (Test-Path "dashboards\seneye-dashboard-mushroom.yaml") {
  Copy-Item -Force -Path "dashboards\seneye-dashboard-mushroom.yaml" -Destination $DashDst
}

Copy-Item -Force -Path "blueprints\automation\seneye\seneye_nh3_high_alert.yaml" -Destination $BpDst
Copy-Item -Force -Path "blueprints\automation\seneye\seneye_data_stale.yaml" -Destination $BpDst
if (Test-Path "blueprints\automation\seneye\seneye_ph_out_of_range.yaml") {
  Copy-Item -Force -Path "blueprints\automation\seneye\seneye_ph_out_of_range.yaml" -Destination $BpDst
}

Write-Host ""
Write-Host "✅ Copied dashboards to: $DashDst"
Write-Host "✅ Copied blueprints to: $BpDst"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1) Dashboards → Settings > Dashboards > Add Dashboard > YAML mode."
Write-Host "   Pick one:"
Write-Host "   - $DashDst\seneye-dashboard.yaml (built-in)"
Write-Host "   - $DashDst\seneye-dashboard-apexcharts.yaml (HACS apexcharts-card)"
Write-Host "   - $DashDst\seneye-dashboard-mushroom.yaml (HACS Mushroom)"
Write-Host "2) Blueprints → Settings > Automations & Scenes > Blueprints → Import → upload from $BpDst"
Write-Host ""
Write-Host "Tip: If using ApexCharts or Mushroom, add their resources in Settings > Dashboards > Resources."
