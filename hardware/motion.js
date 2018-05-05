load('api_config.js');
load('api_events.js');
load('api_gpio.js');
load('api_mqtt.js');
load('api_net.js');
load('api_sys.js');
load('api_timer.js');

let led = Cfg.get('pins.led');
let button = Cfg.get('pins.button');
let pirSensor = 4;
let topic = '/devices/' + Cfg.get('device.id') + '/events';

let getMotionInfo = function() {
  let motion = GPIO.read(pirSensor);
  return JSON.stringify({
    motion: motion === 1 ? 'on' : 'off'
  });
};

GPIO.set_mode(led, GPIO.MODE_OUTPUT);
GPIO.write(led, 1);
GPIO.set_mode(pirSensor, GPIO.MODE_INPUT);

let value = 0;
Timer.set(1000 /* 1 sec */, true /* repeat */, function() {
  let motion = GPIO.read(pirSensor);
  print('motion:', getMotionInfo());
  // value = motion;
  if(value !== motion) {
    value = motion;
    MQTT.pub(topic, getMotionInfo(), 1);
  }
}, null);