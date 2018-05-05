load('api_config.js');
load('api_gpio.js');
load('api_mqtt.js');
load('api_net.js');
load('api_sys.js');
load('api_timer.js');
load('api_dht.js');
load('api_events.js');
load('api_adc.js');


let led_pin = Cfg.get('pins.led');
let button = Cfg.get('pins.button');
let adc_pin = 0;
let topicBase = '/devices/' + Cfg.get('device.id') + '/';
let topic = topicBase + 'events';
let led_topic = topicBase + 'power';

// Initialize ADC
ADC.enable(adc_pin)

// GPIO pin which has a DHT sensor data wire connected
let dht_pin = 13;

// Initialize DHT library
let dht = DHT.create(dht_pin, DHT.DHT22);
GPIO.set_mode(dht_pin, GPIO.MODE_INPUT);

let getInfo = function() {
  let lux = ADC.read(adc_pin);
  let t_celsius = dht.getTemp();
  let temp = 0;
  let heatIndex = 0;
  let h = dht.getHumidity();

  if (isNaN(h)) {
    h = 0
  }
  if (isNaN(t_celsius)) {
    t_celsius = 0
  } else {
    // convert to F
    temp = t_celsius * 1.8 + 32
    
    if (temp >= 80) {
      heatIndex = -42.379 + 2.04901523*temp + 10.14333127*h;
      heatIndex = heatIndex - 0.22475541*temp*h - 0.00683783*temp*temp;
      heatIndex = heatIndex - 0.05481717*h*h + 0.00122874*temp*temp*h;
      heatIndex = heatIndex + 0.00085282*temp*h*h - 0.00000199*temp*temp*h*h;
    } else {
      heatIndex = 0.5 * (temp + 61.0 + ((temp - 68.0)*1.2) + (h * 0.094));
    }
  
    if (h < 13 && 80 <= temp <= 112) {
      let adjustment = ((13-h)/4) * Math.sqrt((17-Math.abs(temp-95.0))/17);
      heatIndex = heatIndex - adjustment;
    }
  }

  return JSON.stringify({
    temperature: t_celsius,
    temp_fahrenheit: temp,
    humidity: h,
    heat_index: heatIndex,
    lux: lux
  });
};

let time = 120000;
let send_info = function() {
  print('uptime:', Sys.uptime(), getInfo());
  MQTT.pub(topic, getInfo(), 1);
};
Timer.set(time, true /* repeat */, send_info, null);
send_info();
