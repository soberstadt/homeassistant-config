for x in range(0, 50):
  hass.services.call('roku_remote', 'press_button', service_data={ 'button': "volume_down" }, blocking=True)

level = data.get('level', 15)
for x in range(0, level):
  hass.services.call('roku_remote', 'press_button', service_data={ 'button': "volume_up" }, blocking=True)
