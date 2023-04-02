import network
import time
import usocket as socket
import hapi.ulog
import hapi.utils
import hapi.html_gen


AP_STATS = {
    1000: "STAT_IDLE",
    1001: "STAT_CONNECTING",
    1010: "STAT_GOT_IP",
    202: "STAT_WRONG_PASSWORD",
    201: "STAT_NO_AP_FOUND"
}


class WebServer:

    def __init__(self, ssid, password, sta_config_path="wifi_config.txt"):
        self._request_counter = 0
        self._ap = network.WLAN(network.AP_IF)
        self._ap.config(essid=ssid, password=password, authmode=4)
        self._ap.active(True)
        time.sleep(2)
        hapi.ulog.show(f"Started Access Point '{ssid}' : {self._ap.ifconfig()}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(("", 80))
        self._socket.setblocking(False)
        self._socket.listen(5)
        self._sta = network.WLAN(network.STA_IF)
        self._sta_config_path = sta_config_path
        self._sta_config = hapi.utils.json_read(self._sta_config_path)
        if self._sta_config:
            self.connect_sta(**self._sta_config)

    def connect_sta(self, ssid, password):
        self._sta_config = dict(ssid=ssid, password=password)
        hapi.ulog.show(f"Connecting to {ssid}")
        self._sta.active(False)
        self._sta.active(True)
        self._sta.connect(ssid, password)
        hapi.utils.wait(self._sta.isconnected)
        if self._sta.isconnected():
            hapi.utils.json_write(self._sta_config_path, self._sta_config)
            hapi.ulog.show(f"Connected to WiFi '{ssid}' : {self._sta.ifconfig()}")
        time.sleep(2)
        hapi.utils.sync_ntp()

    def accept(self, request_handler):
        try:
            conn, addr = self._socket.accept()
            hapi.ulog.show(f"Processing request from {addr}")
            request = conn.recv(1024)
            request = str(request)
            hapi.ulog.show(request, level=hapi.ulog.DEBUG)
            request = request.split(' HTTP/1.1')[0]
            hapi.ulog.show(request)
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
            conn.sendall(request_handler(self, request))
            conn.close()
        except OSError:
            pass
        except Exception as e:
            hapi.ulog.show(f"Exception while processing request: {repr(e)}")

    def status(self):
        return f'''<p>Access Point Configuration:<br>{"<br>".join(self._ap.ifconfig())}</p>
<p>Station Config.:<br>{AP_STATS.get(self._sta.status(), "Invalid")}<br>{"<br>".join(self._sta.ifconfig())}</p>'''

    def install_mcron(self):
        if hapi.utils.exists("/lib/mcron"):
            return True
        if self._sta and self._sta.isconnected():
            import upip
            upip.install("micropython-mcron")
            return True
        return False
