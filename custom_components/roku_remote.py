DOMAIN = 'roku_remote'

LAST_BUTTON_TOPIC = 'last_button'

# import voluptuous as vol
# import homeassistant.helpers.config_validation as cv
from roku import Roku
import logging

def setup(hass, config):
    roku = None

    devices = Roku.discover(timeout=5)
    for d in devices:
        if d.port == 8060: roku = d
        if roku != None: break

    def button_press(call):
        button_name = call.data.get('button', '')
        hass.states.set("{0}.{1}".format(DOMAIN, LAST_BUTTON_TOPIC), button_name)
        getattr(roku, button_name)()

    hass.services.async_register(DOMAIN, 'press_button', button_press)

    return True