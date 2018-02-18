seconds = int(data.get('seconds', 30))

hass.services.call('roku_remote', 'press_button', service_data={ 'button': 'forward' }, blocking=True)

hass.services.call('roku_remote', 'sleep', service_data={ 'time': (seconds/20.0) }, blocking=True)

hass.services.call('roku_remote', 'press_button', service_data={ 'button': 'play' }, blocking=True)