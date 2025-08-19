import logging
from datetime import timedelta, datetime, timezone
from pyseneye.sud import SUDevice, Action

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL_MIN, CONF_TEMP_OFFSET, CONF_PH_OFFSET, CONF_PAR_SCALE,
    DEFAULT_UPDATE_INTERVAL_MIN, DEFAULT_TEMP_OFFSET, DEFAULT_PH_OFFSET, DEFAULT_PAR_SCALE,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor"]
SERVICE_FORCE_UPDATE = "force_update"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    opts = entry.options or {}
    update_minutes = int(opts.get(CONF_UPDATE_INTERVAL_MIN, DEFAULT_UPDATE_INTERVAL_MIN))
    temp_offset = float(opts.get(CONF_TEMP_OFFSET, DEFAULT_TEMP_OFFSET))
    ph_offset = float(opts.get(CONF_PH_OFFSET, DEFAULT_PH_OFFSET))
    par_scale = float(opts.get(CONF_PAR_SCALE, DEFAULT_PAR_SCALE))

    _LOGGER.debug("Seneye options: update=%s, temp_offset=%s, ph_offset=%s, par_scale=%s",
                  update_minutes, temp_offset, ph_offset, par_scale)

    coordinator = SeneyeDataUpdateCoordinator(
        hass, update_minutes=update_minutes,
        temp_offset=temp_offset, ph_offset=ph_offset, par_scale=par_scale
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_force_update_service(call: ServiceCall) -> None:
        _LOGGER.info("Service '%s.%s' called: forcing refresh", DOMAIN, SERVICE_FORCE_UPDATE)
        await coordinator.async_request_refresh()

    async def _update_listener(hass: HomeAssistant, updated: ConfigEntry) -> None:
        _LOGGER.debug("Options changed; reloading Seneye")
        await hass.config_entries.async_reload(updated.entry_id)

    entry.async_on_unload(entry.add_update_listener(_update_listener))
    hass.services.async_register(DOMAIN, SERVICE_FORCE_UPDATE, async_force_update_service)

    _LOGGER.info("Seneye setup complete")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        try:
            hass.services.async_remove(DOMAIN, SERVICE_FORCE_UPDATE)
        except Exception:
            pass
    return unload_ok

class SeneyeDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, update_minutes: int, temp_offset: float, ph_offset: float, par_scale: float) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=update_minutes))
        self.temp_offset = float(temp_offset)
        self.ph_offset = float(ph_offset)
        self.par_scale = float(par_scale)
        self.last_success_utc: datetime | None = None

    async def _async_update_data(self):
        try:
            result = await self.hass.async_add_executor_job(self._get_seneye_data)
            self.last_success_utc = datetime.now(timezone.utc)
            _LOGGER.debug("Seneye poll OK: %s", type(result).__name__)
            return result
        except Exception as err:
            _LOGGER.error("Seneye poll failed: %s", err)
            raise UpdateFailed(f"Error communicating with Seneye device: {err}") from err

    def _get_seneye_data(self):
        device = SUDevice()
        try:
            device.action(Action.ENTER_INTERACTIVE_MODE)
            response = device.action(Action.SENSOR_READING)
            return response
        finally:
            device.close()
