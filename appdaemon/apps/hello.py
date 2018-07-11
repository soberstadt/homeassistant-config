import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")
     self.log("You are now ready to run Apps!")
     self.log("AC is set to: " + self.entities.binary_sensor.ac_running.state)
