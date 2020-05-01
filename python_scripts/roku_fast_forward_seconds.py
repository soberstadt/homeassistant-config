seconds = int(data.get('seconds', 30))

hass.services.call('remote',
                   'send_command',
                   service_data={ 'entity_id': 'remote.roku', 'button': 'forward' },
                   blocking=True)

time.sleep(seconds/20.0)

hass.services.call('remote',
                   'send_command',
                   service_data={ 'entity_id': 'remote.roku', 'button': 'play' },
                   blocking=True)
