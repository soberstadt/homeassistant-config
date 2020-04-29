import logging

import homeassistant.util.color as color_util
from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_COLOR_TEMP,
                                            ATTR_HS_COLOR, SUPPORT_BRIGHTNESS,
                                            SUPPORT_COLOR, SUPPORT_COLOR_TEMP,
                                            Light)
from meross_iot.cloud.client_status import ClientStatus
from meross_iot.cloud.devices.light_bulbs import GenericBulb
from meross_iot.cloud.exceptions.CommandTimeoutException import CommandTimeoutException
from meross_iot.manager import MerossManager
from meross_iot.meross_event import (BulbLightStateChangeEvent,
                                     BulbSwitchStateChangeEvent,
                                     DeviceOnlineStatusEvent)
from .common import (DOMAIN, HA_LIGHT, MANAGER, ConnectionWatchDog, log_exception)
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


def rgb_int_to_tuple(color):
    blue = color & 255
    green = (color >> 8) & 255
    red = (color >> 16) & 255
    return (red, green, blue)


def expand_status(status):
    "Expand the status information for readability"
    out = dict(status)
    out['rgb'] = rgb_int_to_tuple(status['rgb'])
    return out


class LightEntityWrapper(Light):
    """Wrapper class to adapt the Meross switches into the Homeassistant platform"""

    def __init__(self, device: GenericBulb, channel: int):
        self._device = device

        # Device info
        self._id = self._device.uuid
        self._channel_id = channel
        self._available = True  # Assume the mqtt client is connected
        self._first_update_done = False
        self._ignore_update = False

        # Assume this device supports all the following features.
        # If that's not the case, we'll discover it after first UPDATE() occurs
        self._flags = 0
        self._flags |= SUPPORT_BRIGHTNESS
        self._flags |= SUPPORT_COLOR
        self._flags |= SUPPORT_COLOR_TEMP
    
    def update(self):
        if self._ignore_update:
            _LOGGER.warning("Skipping UPDATE as ignore_update is set.")
            return

        if self._device.online:
            try:
                self._device.get_status(force_status_refresh=True)
                self._flags = 0
                if self._device.supports_luminance():
                    self._flags |= SUPPORT_BRIGHTNESS
                if self._device.is_rgb():
                    self._flags |= SUPPORT_COLOR
                if self._device.is_light_temperature():
                    self._flags |= SUPPORT_COLOR_TEMP
                self._first_update_done = True
            except CommandTimeoutException as e:
                log_exception(logger=_LOGGER, device=self._device)
                raise

    def device_event_handler(self, evt):
        # Update the device state as soon as an event occurs
        self.schedule_update_ha_state(False)

        """
        # Handle here events that are common to all the wrappers
        if isinstance(evt, DeviceOnlineStatusEvent):
            _LOGGER.info("Device %s reported online status: %s" % (self._device.name, evt.status))
            if evt.status not in ["online", "offline"]:
                raise ValueError("Invalid online status")
            self._is_online = evt.status == "online"

        elif isinstance(evt, BulbSwitchStateChangeEvent):
            if evt.channel == self._channel_id:
                self._state['onoff'] = evt.is_on
        elif isinstance(evt, BulbLightStateChangeEvent):
            if evt.channel == self._channel_id:
                self._state['capacity'] = evt.light_state.get('capacity')
                self._state['rgb'] = evt.light_state.get('rgb')
                self._state['temperature'] = evt.light_state.get('temperature')
                self._state['luminance'] = evt.light_state.get('luminance')
                self._state['gradual'] = evt.light_state.get('gradual')
                self._state['transform'] = evt.light_state.get('transform')
        else:
            _LOGGER.warning("Unhandled/ignored event: %s" % str(evt))
        """

    def notify_client_state(self, status: ClientStatus):
        # When a connection change occurs, update the internal state
        # If we are connecting back, schedule a full refresh of the device
        # In any other case, mark the device unavailable
        # and only update the UI
        client_online = status == ClientStatus.SUBSCRIBED
        self._available = client_online
        self.schedule_update_ha_state(True)

    @property
    def assumed_state(self) -> bool:
        return not self._first_update_done

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def available(self) -> bool:
        # A device is available if it's online
        return self._available and self._device.online

    @property
    def is_on(self) -> bool:
        if not self._first_update_done:
            # Schedule update and return
            self.schedule_update_ha_state(True)
            return None

        return self._device.get_channel_status(channel=self._channel_id).get('onoff')

    @property
    def brightness(self):
        if not self._first_update_done:
            # Schedule update and return
            self.schedule_update_ha_state(True)
            return None

        # Meross bulbs support luminance between 0 and 100;
        # while the HA wants values from 0 to 255. Therefore, we need to scale the values.
        luminance = self._device.get_status().get('luminance', None)
        if luminance is None:
            return None
        return float(luminance) / 100 * 255

    @property
    def hs_color(self):
        if not self._first_update_done:
            # Schedule update and return
            self.schedule_update_ha_state(True)
            return None

        status = self._device.get_status(channel=self._channel_id)
        if status.get('capacity') == 5:  # rgb mode
            rgb = rgb_int_to_tuple(status.get('rgb'))
            return color_util.color_RGB_to_hs(*rgb)
        return None

    @property
    def color_temp(self):
        if not self._first_update_done:
            # Schedule update and return
            self.schedule_update_ha_state(True)
            return None

        status = self._device.get_status(channel=self._channel_id)
        if status.get('capacity') == 6:  # White light mode
            value = status.get('temperature')
            norm_value = (100 - value) / 100.0
            return self.min_mireds + (norm_value * (self.max_mireds - self.min_mireds))
        return None

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def supported_features(self):
        return self._flags

    @property
    def device_info(self):
        return {
            'identifiers': {(DOMAIN, self._id)},
            'name': self._device.name,
            'manufacturer': 'Meross',
            'model': self._device.type + " " + self._device.hwversion,
            'sw_version': self._device.fwversion
        }

    def turn_off(self, **kwargs) -> None:
        self._device.turn_off(channel=self._channel_id)

    def turn_on(self, **kwargs) -> None:
        if not self.is_on:
            self._device.turn_on(channel=self._channel_id)

        # Color is taken from either of these 2 values, but not both.
        if ATTR_HS_COLOR in kwargs:
            h, s = kwargs[ATTR_HS_COLOR]
            rgb = color_util.color_hsv_to_RGB(h, s, 100)
            _LOGGER.debug("color change: rgb=%r -- h=%r s=%r" % (rgb, h, s))
            self._device.set_light_color(self._channel_id, rgb=rgb)
        elif ATTR_COLOR_TEMP in kwargs:
            mired = kwargs[ATTR_COLOR_TEMP]
            norm_value = (mired - self.min_mireds) / (self.max_mireds - self.min_mireds)
            temperature = 100 - (norm_value * 100)
            _LOGGER.debug("temperature change: mired=%r meross=%r" % (mired, temperature))
            self._device.set_light_color(self._channel_id, temperature=temperature)

        # Brightness must always be set, so take previous luminance if not explicitly set now.
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS] * 100 / 255
            _LOGGER.debug("    brightness change: %r" % brightness)
            self._device.set_light_color(self._channel_id, luminance=brightness)

    async def async_added_to_hass(self) -> None:
        self._device.register_event_callback(self.device_event_handler)
        self._ignore_update = False

    async def async_will_remove_from_hass(self) -> None:
        self._device.unregister_event_callback(self.device_event_handler)
        self._ignore_update = True


async def async_setup_entry(hass, config_entry, async_add_entities):
    def sync_logic():
        bulb_devices = []
        manager = hass.data[DOMAIN][MANAGER]  # type:MerossManager
        bulbs = manager.get_devices_by_kind(GenericBulb)

        for bulb in bulbs:
            w = LightEntityWrapper(device=bulb, channel=0)
            bulb_devices.append(w)
            hass.data[DOMAIN][HA_LIGHT][w.unique_id] = w
        return bulb_devices

    # Register a connection watchdog to notify devices when connection to the cloud MQTT goes down.
    manager = hass.data[DOMAIN][MANAGER]  # type:MerossManager
    watchdog = ConnectionWatchDog(hass=hass, platform=HA_LIGHT)
    manager.register_event_handler(watchdog.connection_handler)
    bulb_devices = await hass.async_add_executor_job(sync_logic)
    async_add_entities(bulb_devices, True)


def setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass
