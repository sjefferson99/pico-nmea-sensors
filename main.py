import config
import network
import socket
import time
import math
import rp2
import ubinascii
from nmea import xdr
import random

def reconnect_wifi(ssid, password, country):

    start_ms = time.ticks_ms()

    # Set country
    rp2.country(country)

    # Reference: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
    CYW43_LINK_DOWN = 0
    CYW43_LINK_JOIN = 1
    CYW43_LINK_NOIP = 2
    CYW43_LINK_UP = 3
    CYW43_LINK_FAIL = -1
    CYW43_LINK_NONET = -2
    CYW43_LINK_BADAUTH = -3

    status_names = {
        CYW43_LINK_DOWN: "Link is down",
        CYW43_LINK_JOIN: "Connected to wifi",
        CYW43_LINK_NOIP: "Connected to wifi, but no IP address",
        CYW43_LINK_UP: "Connect to wifi with an IP address",
        CYW43_LINK_FAIL: "Connection failed",
        CYW43_LINK_NONET: "No matching SSID found (could be out of range, or down)",
        CYW43_LINK_BADAUTH: "Authenticatation failure",
    }

    wlan = network.WLAN(network.STA_IF)

    def wlog(message):
        print(f"[WLAN] {message}")

    def dump_status():
        status = wlan.status()
        wlog(f"active: {1 if wlan.active() else 0}, status: {status} ({status_names[status]})")
        return status

    def wait_status(expected_status, *, timeout=10, tick_sleep=0.5):
        for i in range(math.ceil(timeout / tick_sleep)):
            time.sleep(tick_sleep)
            status = dump_status()
            if status == expected_status:
                return True
            if status < 0:
                raise Exception(status_names[status])
        return False

    wlan.active(True)
    # Disable power saving mode - TODO only do this on USB power/config option
    wlan.config(pm=0xa11140)

    # Print MAC
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    wlog("MAC: " + mac)
    
    # Disconnect when necessary
    status = dump_status()
    if status >= CYW43_LINK_JOIN and status <= CYW43_LINK_UP:
        wlog("Disconnecting...")
        wlan.disconnect()
        try:
            wait_status(CYW43_LINK_DOWN)
        except Exception as x:
            raise Exception(f"Failed to disconnect: {x}")
    wlog("Ready for connection!")

    # Connect to our AP
    wlog(f"Connecting to SSID {ssid} (password: {password})...")
    wlan.connect(ssid, password)
    try:
        wait_status(CYW43_LINK_UP)
    except Exception as x:
        raise Exception(f"Failed to connect to SSID {ssid} (password: {password}): {x}")
    wlog("Connected successfully!")

    ip, subnet, gateway, dns = wlan.ifconfig()
    wlog(f"IP: {ip}, Subnet: {subnet}, Gateway: {gateway}, DNS: {dns}")
    
    elapsed_ms = time.ticks_ms() - start_ms
    wlog(f"Elapsed: {elapsed_ms}ms")
    return wlan, elapsed_ms

def connect_to_wifi() -> network.WLAN:
    print(f"> connecting to wifi network '{config.wifi_ssid}'")
    wlan, elapsed_ms = reconnect_wifi(config.wifi_ssid, config.wifi_password, config.wifi_country)
    # a slow connection time will drain the battery faster and may
    # indicate a poor quality connection
    seconds_to_connect = elapsed_ms / 1000
    if seconds_to_connect > 5:
        print("  - took", seconds_to_connect, "seconds to connect to wifi")
    return wlan


wlan = connect_to_wifi()
wlan_ip = wlan.ifconfig()[0]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.bind((wlan_ip, 2000))
server.listen(1)
print(server)
connections = []

nmea_weather = xdr()

while True:
    try:
        connection, address = server.accept()
        connection.setblocking(False)
        connections.append(connection)
    except:
        pass

    for connection in connections:
        sentence = nmea_weather.send_weather_data(random.randint(-50,450) / 10, random.randint(9500,10500) / 10000, random.randint(20,100))
        connection.send(sentence)
    
    time.sleep(5)