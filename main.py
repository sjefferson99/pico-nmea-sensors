from nmea import xdr

nmea_weather = xdr()

sentence = nmea_weather.send_weather_data(19.1, 1012.4, 49)

print(sentence)