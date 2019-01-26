seconds = int(data.get('seconds', 30))

hass.services.call('remote',
                   'send_command',
                   service_data={ 'entity_id': 'remote.roku', 'button': 'forward' },
                   blocking=True)

hass.services.call('roku_remote', 'sleep', service_data={ 'time': (seconds/20.0) }, blocking=True)

hass.services.call('remote',
                   'send_command',
                   service_data={ 'entity_id': 'remote.roku', 'button': 'play' },
                   blocking=True)
