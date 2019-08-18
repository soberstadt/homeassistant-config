for x in range(0, 50):
  hass.services.call('remote',
                     'send_command',
                     service_data={ 'entity_id': "remote.roku", 'command': "volume_down" },
                     blocking=True)

level = data.get('level', 15)
for x in range(0, level):
  hass.services.call('remote',
                     'send_command',
                     service_data={ 'entity_id': "remote.roku", 'command': "volume_up" },
                     blocking=True)
