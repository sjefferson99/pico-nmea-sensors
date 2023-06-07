# Pico NMEA Sensors

Simple solution to collect I2C sensor data and publish on a TCP socket in NMEA 0183 format for use on boats.
This module requires the use of a Pico W and will need to be connected to a wireless access point.

## Supported sensors
- BME280 - Temperature, humidity and pressure

## Hardware configuration
Pico W board, ideally connected to USB power for continuous output
BME280 module connected over I2C - refer to [pico pinout ](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

## Software configuration
Load Pimoroni micropython firmware - this code was built against [v1.20.2](https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.20.2)
Load all repo files onto the Pico using Thonny or equivalent program
Adjust config.py with appropriate values:
- Wireless info - Your SSID and wifi password
- NMEA config - the TCP port you want to send NMEA data over
- I2C - The pins you have connected the sensors to for I2C - default is Pins 0 and 1 (refer to pinout above) - I2C 0 is hardcoded at present.

Reset board to execute the program and start outputting NMEA weather data

## Testing and connecting boat instruments
The wifi connection uses DHCP, so either make a MAC reservation on your router/DHCP server, look up the connected clients on your router/DHCP server or monitor the pico debug output via USB for the IP address to connect to.
The TCP port is as configured above.
For a quick test on a windows command line enter:
```
telnet <ip address> <TCP port>
```
You should see NMEA weather data appear once every 5 seconds.
### Example:
```
$YXXDR,C,18.92,C,AIRTEMP,P,1.01272,B,BARO,H,52.64,P,HUMIDITY*3A
```
<p>
You can now connect devices such as OpenCPN to the IP and TCP port above to populate temperatire, humidity and pressure information.
</p>
<p>
<b>Warning - at present the socket code is very basic and only supports one client connecting at a time and will crash the board when a client disconnects. If in doubt, reset the board if you are not able to connect to the TCP socket.</b>
</p>