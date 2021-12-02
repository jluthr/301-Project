import board
import busio
import analogio
import digitalio
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import time

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

esp32_cs = digitalio.DigitalInOut(board.D13)
esp32_ready = digitalio.DigitalInOut(board.D11)
esp32_reset = digitalio.DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)



if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

print("Connecting to AP...")
esp.connect_AP(secrets['ssid'], secrets['password'])
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
print("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
print("Ping google.com: %d ms" % esp.ping("google.com"))
#--------------------------------------------------

readValue = analogio.AnalogIn(board.A0)
led = digitalio.DigitalInOut(board.D5)
led.direction = digitalio.Direction.OUTPUT

def analog_voltage(pin):
    return (pin.value / 65536) * 3.3

# POSTING DATA
while True:
    # Read the value, then the voltage.
    val = readValue.value
    volts = analog_voltage(readValue)
    # Print the values:
    print('Sensor value: {0} Turbidity: {1}V'.format(val, volts))
    if volts < 4:
        led.value = True
    else:
        led.value = False
    #volts= str(volts)
    conversion = volts*2.361
    print("CHEAT CODE = " + str(conversion))
    tds_val = (-1120.4*(conversion**2)) + (5742.3*conversion) - 4352.9
    if tds_val < 0:
        tds_val = 0
    tds_val = str(tds_val)
    print("Turbidity value (mg/L)" + tds_val)
    JSON_POST_URL = "https://api.thingspeak.com/update?api_key=8MPW4DVTLBMV16NZ&field1="+ tds_val
    print("POSTing data to {0}: {1}".format(JSON_POST_URL, tds_val))
    response = requests.post(JSON_POST_URL, data=tds_val)
    print('-'*40)
    time.sleep(5)
    json_resp = response.json()
    #print("Data received from server:", json_resp['data'])
    response.close()
    time.sleep(5)
'''
print('-'*40)
response.close()
data = '31F'
print("POSTing data to {0}: {1}".format(JSON_POST_URL, data))
response = requests.post(JSON_POST_URL, data=data)
print('-'*40)

json_resp = response.json()
# Parse out the 'data' key from json_resp dict.
print("Data received from server:", json_resp['data'])
print('-'*40)
response.close()
'''
