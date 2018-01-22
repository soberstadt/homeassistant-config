DOMAIN = 'roku_remote'

LAST_BUTTON_TOPIC = 'last_button'
LAST_IP_STATE_NAME = 'input_text.roku_remote_ip'

from roku import Roku
import logging
import time

def setup(hass, config):
    roku = None

    def find_roku():
        logging.info('[roku_remote] looking for devices')
        devices = Roku.discover(timeout=5)
        logging.info('[roku_remote] found: ')
        logging.info(devices)
        found = None;

        for d in devices:
            if d.port == 8060: found = d
            if found != None: break
        if found != None: 
            roku = found
            hass.states.set(LAST_IP_STATE_NAME, roku.host)
            logging.info('[roku_remote] selected:')
            logging.info(roku)
        else:
            logging.error('[roku_remote] no roku found')

        return found

    # connect to a roku at start-up
    if find_roku() == None:
        roku = Roku(hass.states.get(LAST_IP_STATE_NAME).state)

    def button_press(call):
        button_name = call.data.get('button', '')
        hass.states.set("{0}.{1}".format(DOMAIN, LAST_BUTTON_TOPIC), button_name)
        try:
            getattr(roku, button_name)()
        except Exception as e:
            if find_roku() != None: getattr(roku, button_name)()


    hass.services.async_register(DOMAIN, 'press_button', button_press)

    return True
