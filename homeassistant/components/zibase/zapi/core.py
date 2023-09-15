"""Librairie Python pour la ZiBase."""
from datetime import datetime
import logging
import socket
import struct
import urllib

import defusedxml.ElementTree as ET

_LOGGER = logging.getLogger(__name__)


class ZbProtocol:
    """Protocoles compatibles Zibase."""

    PRESET = 0
    VISONIC433 = 1
    VISONIC868 = 2
    CHACON = 3
    DOMIA = 4
    X10 = 5
    ZWAVE = 6
    RFS10 = 7
    X2D433 = 8
    X2D868 = 9


class ZbAction:
    """Action possible de la zibase."""

    OFF = 0
    ON = 1
    DIM_BRIGHT = 2
    ALL_LIGHTS_ON = 4
    ALL_LIGHTS_OFF = 5
    ALL_OFF = 6
    ASSOC = 7


def create_zb_calendar_from_integer(data):
    """Create a ZbCalendar object from an int coming from zibase."""
    cal = ZbCalendar()
    for i in range(24):
        cal.hour[i] = (data & (1 << i)) >> i

    cal.day["lundi"] = (data & (1 << 24)) >> 24
    cal.day["mardi"] = (data & (1 << 25)) >> 25
    cal.day["mercredi"] = (data & (1 << 26)) >> 26
    cal.day["jeudi"] = (data & (1 << 27)) >> 27
    cal.day["vendredi"] = (data & (1 << 28)) >> 28
    cal.day["samedi"] = (data & (1 << 29)) >> 29
    cal.day["dimanche"] = (data & (1 << 30)) >> 30
    return cal


class ZbCalendar:
    """Repr�sente une variable calendrier de la zibase."""

    def __init__(self):
        """Calendar initialization."""
        self.hour = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
        self.day = {
            "lundi": 0,
            "mardi": 0,
            "mercredi": 0,
            "jeudi": 0,
            "vendredi": 0,
            "samedi": 0,
            "dimanche": 0,
        }

    def to_integer(self):
        """Retourne l'entier 32bits repr�sentant ce calendrier."""
        data = 0x00000000
        for i in range(24):
            data |= self.hour[i] << i

        data |= self.day["lundi"] << 24
        data |= self.day["mardi"] << 25
        data |= self.day["mercredi"] << 26
        data |= self.day["jeudi"] << 27
        data |= self.day["vendredi"] << 28
        data |= self.day["samedi"] << 29
        data |= self.day["dimanche"] << 30
        return data


class ZbRequest:
    """Repr�sente une requ�te � la zibase."""

    def __init__(self):
        """Request initialization."""
        self.header = bytearray("ZSIG", "utf-8")
        self.command = 0
        self.reserved1 = ""
        self.zibase_id = ""
        self.reserved2 = ""
        self.param1 = 0
        self.param2 = 0
        self.param3 = 0
        self.param4 = 0
        self.my_count = 0
        self.your_count = 0
        self.message = ""

    def to_binary_array(self):
        """Serialize la requ�te en chaine binaire."""

        buffer = self.header
        buffer.extend(struct.pack("!H", self.command))
        buffer.extend(bytes(self.reserved1.rjust(16, chr(0)), "utf-8"))
        buffer.extend(bytes(self.zibase_id.rjust(16, chr(0)), "utf-8"))
        buffer.extend(bytes(self.reserved2.rjust(12, chr(0)), "utf-8"))
        buffer.extend(struct.pack("!I", self.param1))
        buffer.extend(struct.pack("!I", self.param2))
        buffer.extend(struct.pack("!I", self.param3))
        buffer.extend(struct.pack("!I", self.param4))
        buffer.extend(struct.pack("!H", self.my_count))
        buffer.extend(struct.pack("!H", self.your_count))
        if len(self.message) > 0:
            buffer.extend(self.message.ljust(96, chr(0)))

        # buffer = array('B')
        # buffer.append(90)
        # buffer.append(83)
        # buffer.append(73)
        # buffer.append(71)
        # buffer.append(0)
        # buffer.append(11)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(3)
        # buffer.append(1)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        # buffer.append(0)
        return buffer


class ZbResponse:
    """Zibase response representation."""

    def __init__(self, buffer):
        """Response builder from received binary string."""
        self.header = buffer[0:4]
        self.command = struct.unpack("!H", buffer[4:6])[0]
        self.reserved1 = buffer[6:22]
        self.zibase_id = buffer[22:38]
        self.reserved2 = buffer[38:50]
        self.param1 = struct.unpack("!I", buffer[50:54])[0]
        self.param2 = struct.unpack("!I", buffer[54:58])[0]
        self.param3 = struct.unpack("!I", buffer[58:62])[0]
        self.param4 = struct.unpack("!I", buffer[62:66])[0]
        self.my_count = struct.unpack("!H", buffer[66:68])[0]
        self.your_count = struct.unpack("!H", buffer[68:70])[0]
        self.message = buffer[70:]


class ZiBase:
    """core class to communicate with Zibase."""

    def __init__(self, ip):
        """Indiquer l'adresse IP de la ZiBase."""
        self.ip = ip
        self.port = 49999

    def send_request(self, request):
        """Send request to zibase via the network."""

        _LOGGER.debug("Send request#IP_ZIBASE=%s", self.ip)
        buffer = request.to_binary_array()
        response = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.connect((self.ip, self.port))
        # buffer = bytes("ZSIG", "utf-8")

        sock.send(buffer)
        ack = sock.recv(512)
        _LOGGER.info("Send srequest#ACK=%s", ack)
        if len(ack) > 0:
            response = ZbResponse(ack)
        sock.close()
        return response

    def send_command(
        self, address, action, protocol=ZbProtocol.PRESET, dim_level=0, nb_burst=1
    ):
        """Send command to zibase."""

        _LOGGER.info("Send command#address=%s", address)
        if len(address) >= 2:
            address = address.upper()
            req = ZbRequest()
            req.command = 11
            if action == ZbAction.DIM_BRIGHT and dim_level == 0:
                action = ZbAction.OFF
            req.param2 = action
            req.param2 |= (protocol & 0xFF) << 0x08
            if action == ZbAction.DIM_BRIGHT:
                req.param2 |= (dim_level & 0xFF) << 0x10
            if nb_burst > 1:
                req.param2 |= (nb_burst & 0xFF) << 0x18
            req.param3 = int(address[1:]) - 1
            req.param4 = ord(address[0]) - 0x41
            self.send_request(req)

    def run_scenario(self, num_scenario):
        """Lance le scenario sp�cifi� par son num�ro."""

        req = ZbRequest()
        req.command = 11
        req.param1 = 1
        req.param2 = num_scenario
        self.send_request(req)

    def get_variable(self, num_var):
        """Recupere la valeur d'une variable Vx de la Zibase."""
        req = ZbRequest()
        req.command = 11
        req.param1 = 5
        req.param3 = 0
        req.param4 = num_var
        res = self.send_request(req)
        if res is not None:
            return res.param1
        return None

    def get_state(self, address):
        """Retrieve sensor state.

        Zibase eclusively receives RF orders. It does not reveice CPL X10 ordres.
        So the X10 state of a sensor can be errorful
        """
        if len(address) > 0:
            address = address.upper()
            req = ZbRequest()
            req.command = 11
            req.param1 = 5
            req.param3 = 4

            house_code = ord(address[0]) - 0x41
            device = int(address[1:]) - 1
            req.param4 = device
            req.param4 |= (house_code & 0xFF) << 0x04

            res = self.send_request(req)
            if res is not None:
                return res.param1
            return None

    def set_variable(self, num_var, value):
        """Met � jour une variable zibase avec la valeur sp�cifi�e.

        variable comprise entre 0 et 19.
        """
        req = ZbRequest()
        req.command = 11
        req.param1 = 5
        req.param3 = 1
        req.param4 = num_var
        req.param2 = value & 0xFFFF
        self.send_request(req)

    def get_calendar(self, num_cal):
        """R�cup�re la valeur d'un calendrier dynamique de la Zibase.

        Num�ro de calendrier compris entre 1 et 16.
        """
        req = ZbRequest()
        req.command = 11
        req.param1 = 5
        req.param3 = 2
        req.param4 = num_cal - 1
        res = self.send_request(req)
        if res is not None:
            return create_zb_calendar_from_integer(res.param1)
        return None

    def set_calendar(self, num_cal, calendar):
        """Met � jour le contenu d'un calendrier dynamique de la zibase.

        Num�ro du calendrier compris entre 1 et 16.
        """
        req = ZbRequest()
        req.command = 11
        req.param1 = 5
        req.param3 = 3
        req.param4 = num_cal - 1
        req.param2 = calendar.toInteger()
        self.send_request(req)

    def exec_script(self, script):
        """Execute a zibase script.

        Ex: lm [scenario name] (= launch the scenario "scenario name")
        Ex: lm 2 aft 3600 (= launch the scenario 2 in one hour)
        Ex : lm [test1].lm [test2] (= launch test1 then test2).
        """
        if len(script) > 0:
            req = ZbRequest()
            req.command = 16
            req.message = "cmd: " + script
            self.send_request(req)

    def get_sensor_info(self, id_sensor):
        """Retourne les valeurs v_1 et v_2 du capteur sp�cifi�.

        ainsi que la date heure du relev�.
        Pour les sondes Oregon et TS10, il faut diviser v_1 par 10.
        Tableau en retour :
        index 0 => date du relev�
        index 1 => v_1
        index 2 => v_2.
        """
        if len(id_sensor) > 0:
            url = "http://" + self.ip + "/sensors.xml"
            with urllib.request.urlopen(url) as handle:
                xml_content = handle.read()
                handle.close()
                sensor_type = id_sensor[0:2]
                number = id_sensor[2:]
                xml_doc = ET.fromstring(xml_content)
                nodes = xml_doc.getElementsByTagName("ev")
                for node in nodes:
                    if (
                        node.getAttribute("pro") == sensor_type
                        and node.getAttribute("id") == number
                    ):
                        v_1 = int(node.getAttribute("v_1"))
                        v_2 = int(node.getAttribute("v_2"))
                        date_time = datetime.fromtimestamp(
                            int(node.getAttribute("gmt"))
                        )
                        info = [date_time, v_1, v_2]
                        return info
