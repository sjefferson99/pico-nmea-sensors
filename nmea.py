# Sources for NMA sentence construction:
# https://gpsd.gitlab.io/gpsd/NMEA.html#_xdr_transducer_measurement
# https://www.eye4software.com/hydromagic/documentation/articles-and-howtos/handling-nmea0183-xdr/

import pprint

class nmea:
    """
    Library for creating NMEA sentences from sensor data.
    """
    def __init__(self) -> None:
        self.talker_ids = {
            "$AI":"Alarm Indicator, (AIS?)",
            "$AP":"Auto Pilot (pypilot?)",
            "$BD":"BeiDou (China)",
            "$CD":"Digital Selective Calling (DSC)",
            "$EC":"Electronic Chart Display & Information System (ECDIS)",
            "$GA":"Galileo Positioning System",
            "$GB":"BeiDou (China)",
            "$GI":"NavIC, IRNSS (India)",
            "$GL":"GLONASS, according to IEIC 61162-1",
            "$GN":"Combination of multiple satellite systems (NMEA 1083)",
            "$GP":"Global Positioning System receiver",
            "$GQ":"QZSS regional GPS augmentation system (Japan)",
            "$HC":"Heading/Compass",
            "$HE":"Gyro, north seeking",
            "$II":"Integrated Instrumentation",
            "$IN":"Integrated Navigation",
            "$LC":"Loran-C receiver (obsolete)",
            "$Pxxx":"Proprietary (Vendor specific)",
            "$PQ":"QZSS (Quectel Quirk)",
            "$QZ":"QZSS regional GPS augmentation system (Japan)",
            "$SD":"Depth Sounder",
            "$ST":"Skytraq",
            "$TI":"Turn Indicator",
            "$YX":"Transducer",
            "$WI":"Weather Instrument"
        }
        self.sentence_ids = {
            "XDR":"Transducer Measurement"        
        }
        return None

    def construct_sentence(self, talkerid: str, sentenceid: str, payload: list) -> str:
        """
        Concats talker id, sentence id and payload into CSV string with
        computer CRC, ready to send as NMEA data.
        """
        sentence = talkerid + sentenceid
        for item in payload:
            sentence += "," + str(item)
        checksum = self.create_checksum(sentence)
        sentence += checksum +"\n"
        if len(sentence) > 82:
            print("Sentence too long")
            return -1
        return sentence.upper()
    
    def create_checksum(self, sentence: str) -> str: #TODO actually create a checksum
        crc = 0
        for char in sentence[1:]:
            crc = crc ^ ord(char)
        crc = hex(crc)[2:]
        checksum = "*" + f"{crc:02}"
        return checksum
    
    def get_talker_ids(self, print: bool=False) -> dict:
        """
        Return valid talker IDs, optionally also pretty print to stdout
        """
        if print:
            self.pprint_dict(self.talker_ids)
        return self.talker_ids   

    def get_sentence_ids(self, print: bool=False) -> dict:
        """
        Return valid sentence IDs, optionally also pretty print to stdout
        """
        if print:
            self.pprint_dict(self.sentence_ids)
        return self.sentence_ids
    
    def pprint_dict(self, dict_data: dict) -> None:
        """
        Pretty prints a dictionary
        """
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(dict_data)
        return None

class xdr:
    """
    Class for generating NMEA sentences for transducer measurements
    """
    def __init__(self) -> None:
        self.nm = nmea()
        self.transducer_types = {
            "A":"Angular displacement",
            "C":"Temperature",
            "D":"Depth",
            "F":"Frequency",
            "H":"Humidity",
            "N":"Force",
            "P":"Pressure",
            "R":"Flow"
        }
        self.units = {
            "A ":" Amperes",
            "B ":" Bars",
            "B ":" Binary",
            "C ":" Celsius",
            "D ":" Degrees",
            "H ":" Hertz",
            "I ":" liters/second",
            "K ":" Kelvin",
            "K ":" kg/m3",
            "M ":" Meters",
            "M ":" cubic Meters",
            "N ":" Newton",
            "P ":" Percentage of full range",
            "P ":" Pascal",
            "R ":" RPM",
            "S ":" Parts per thousand",
            "V ":" Volts"
        }
        self.xdr_payload = []
        return None
    
    def get_transducer_types(self, print: bool=False) -> dict:
        """
        Return valid transducer types, optionally also pretty print to stdout
        """
        if print:
            self.nm.pprint_dict(self.transducer_types)
        return self.talker_ids
    
    def get_units(self, print: bool=False) -> dict:
        """
        Return valid units, optionally also pretty print to stdout
        """
        if print:
            self.nm.pprint_dict(self.units)
        return self.talker_ids
    
    def construct_xdr_sentence(self, talkerid: str, payload: list) -> str:
        """
        Construct a valid NMEA setence given XDR payload data:
        transducer type, measurement, unit and data source name, repeated for
        each data source.

        Defaults to using payload data generated by append_xdr_payload()
        Use clear_xdr_payload() to reset this data without sending.

        Use get_transducer_types() and get_units() for valid options
        """
        nm = nmea()
        
        if payload == []:
            payload = self.xdr_payload
        
        output = nm.construct_sentence(talkerid, "XDR", payload)
        self.clear_xdr_payload
        return output
    
    def append_xdr_payload(self, transducer_type: str, measurement: float, unit: str, name: str) -> list:
        """
        Append data to the current XDR payload ready to send as one sentence
        Measurement is a decimal number
        Name is a short string to identify the data source e.g. airtemp or pressure
        Returns the new full XDR payload ready to send for information, this is
        stored in the class and does not need to be passed back.
        """
        self.xdr_payload.append(str(transducer_type))
        self.xdr_payload.append(str(measurement))
        self.xdr_payload.append(str(unit))
        self.xdr_payload.append(str(name))
        return self.xdr_payload
    
    def clear_xdr_payload(self) -> int:
        self.xdr_payload = []
        return 0

    def send_weather_data(self, temperature: float, pressure: float, humidity: float) -> str:
        """
        Create an XDR NMEA sentence for weather data.
        Temperature in degrees Celsuis, Pressure in hPa and relative humidity in %
        """
        self.append_xdr_payload("C", temperature, "C", "AIRTEMP")
        self.append_xdr_payload("P", (pressure / 100), "P", "PRESSURE")
        self.append_xdr_payload("H", humidity, "P", "HUMIDITY")
        sentence = self.construct_xdr_sentence("$WI", self.xdr_payload)
        return sentence