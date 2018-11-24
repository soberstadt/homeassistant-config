from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
from ..meross import DATA_DEVICES, MerossDevice


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Meross Switch device."""
    if discovery_info is None:
        return
    meross_devices = hass.data[DATA_DEVICES]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = None
        for m_device in meross_devices:
            if m_device.device_id() == dev_id:
                device = m_device
                continue
        if device is None:
            continue
        devices.append(MerossSwitch(device))
    add_entities(devices)


class MerossSwitch(MerossDevice, SwitchDevice):
    """meross Switch Device."""

    def __init__(self, meross):
        """Init Meross switch device."""
        super().__init__(meross)
        self.entity_id = ENTITY_ID_FORMAT.format(meross.device_id())

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.meross.get_status()

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.meross.turn_on()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.meross.turn_off()