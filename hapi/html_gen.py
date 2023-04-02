import utime

import hapi.utils
import hapi.signals

PAGE_HEADER = """<html><head><title>Hapi Web Server</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"><style>
html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
h1{color: #0F3376; padding: 2vh;}
p{font-size: 1em;}
.button{font-size: 1.5em; display: inline-block; background-color: #e7bd3b; border: none; border-radius: 6px;
color: white; text-decoration: none; margin: 2px; cursor: pointer;}
.buttonON{background-color: #4286f4;}
.buttonPassive{background-color: #bcbcbc;}
.buttonOFF{background-color: #cc0000;}
</style></head><body><h1>Hapi Web Server</h1>"""


def _clockize(t, lim):
    if t < 0:
        t += lim
    t = str(t)
    if len(t) == 1:
        t = "0" + t
    return t


def clock(hms):
    return f"{_clockize(hms[0] - 3, 24)}:{_clockize(hms[1], 60)}:{_clockize(hms[2], 60)}"


def button(msg, ref=None, b_class=""):
    ref = ref or msg
    return f'<a href="/{ref}"><button class="button{b_class}">{msg}</button></a>'


def on_off_button(name, value):
    a, b = ("ON", "Passive") if value else ("Passive", "OFF")
    return f'''<p><strong>{name}</strong> : <a href="/{name}/enable/"><button class="button button{a}">
ON</button></a><a href="/{name}/disable/"><button class="button button{b}">OFF</button></a></p>'''


def signal(_signal, value):
    if "_Out" in _signal:
        a, b = ("ON", "Passive") if not value else ("Passive", 'OFF')
        _html = button("ON", f'Manual/?{_signal}=ON', f' button{a}')
        _html += button("OFF", f'Manual/?{_signal}=OFF', f' button{b}')
    else:
        _html = "---" if value else "Pressed"
    return f'<p><strong>{_signal}</strong> - ' + _html + '</p>'


def get_page(ws, request):
    _bs = ["Manual", "Cronograma", "WiFi", "Sistema"]
    _html = PAGE_HEADER + f"<p>{''.join(button(_b) for _b in _bs)}</p>"
    if '/Manual' in request:
        if '/Manual/?' in request:
            obj, state = request.split('/Manual/?')[-1].split('=')
            hapi.signals.pin[obj].value(0 if state == "ON" else 1)
        for pin_name in sorted(hapi.signals.pin.keys()):
            _html += signal(pin_name, hapi.signals.pin[pin_name].value())
    elif '/Cronograma' in request:
        try:
            _html += _get_schedules(ws, request)
        except Exception as e:
            hapi.ulog.show(repr(e), level=hapi.ulog.CRITICAL)
    elif "/Sistema" in request:
        for f in hapi.utils.rlistdir():
            _html += f'<p><a href="/Sistema/?file={f}">{f}</a></p>'

        if "/?file=" in request:
            _target_f = request.split("/?file=")[-1].split("&")[0]
            if hapi.utils.exists(_target_f):
                with open(_target_f) as f:
                    _text = f.read().replace("<", "&lt;").replace(">", "&gt;")
            else:
                _text = f"Invalid path: {_target_f}"
            _html += f'<br><br><textarea name="content" cols="100" rows="40">{_text}</textarea>'
    elif "/WiFi" in request:
        _html += ws.status() + '''<form action="/WiFi/connect/"><label for="fname">SSID:</label>
        <input type="text" id="SSID" name="SSID", size=15><br><label for="h">PASS:</label>
        <input type="password" id="PASS" name="PASS", size=15><br><input type="submit" value="Conectar"></form>'''
        if "/WiFi/connect/" in request:
            args = [a.split("=")[1] for a in request.split('/WiFi/connect/?')[-1].split('&')]
            hapi.ulog.show(f"Station connecting to {args}")
            ws.connect_sta(*args)
    return _html + "</body></html>"


def _get_schedules(ws, request):
    if not ws.install_mcron():
        return "<p>Por favor conecte a um WiFi com conexao a internet.</p>"
    from hapi import schedule

    if '/Cronograma/?' in request:
        obj, state = request.split('/Cronograma/?')[-1].split('=')
        if state == "Remove" and obj in schedule.mcron.callback_table:
            schedule.mcron.remove(obj)
            hapi.utils.json_delete_key(schedule.SCHEDULE_FILE, obj)
    if '/Cronograma/add/?' in request:
        args = request.split('/Cronograma/add/?')[-1].split('&')
        args = [int(a.split("=")[1]) for a in args]
        schedule.add_schedule(*args)
    if '/Cronograma/sync/' in request:
        hapi.utils.sync_ntp()
    elif '/Cronograma/enable/' in request:
        schedule.SCHEDULE_ENABLED = True
        print(f"SCHEDULE_ENABLED: {schedule.SCHEDULE_ENABLED}")
    elif '/Cronograma/disable/' in request:
        schedule.SCHEDULE_ENABLED = False
        print(f"SCHEDULE_ENABLED: {schedule.SCHEDULE_ENABLED}")
    html = f"<p>{clock(utime.localtime()[3:6])}</p>"
    html += f'{button("Sync Time", "Cronograma/sync")}'
    html += f'{on_off_button("Cronograma", schedule.SCHEDULE_ENABLED)}'
    for _k in sorted(schedule.mcron.callback_table.keys()):
        if "Step_V" != _k[:6]:
            continue
        _info = _k.split("_")
        _t = hapi.utils.json_read(schedule.SCHEDULE_FILE).get(_k)
        _s = f"{_info[1]} liga as {clock((int(_info[2]) + 3, int(_info[3]), 0))[:-3]} por {_t} min."
        html += f'<p>{_s} {button("Del", "Cronograma/?" + _k + "=Remove")}</p>'
    html += f'''<form action="/Cronograma/add/"><label for="fname">Valve:</label>
<input type="text" id="fname" name="fname", maxlength=1, size=1><br><label for="h">Time:</label>
<input type="text" id="h" name="h", maxlength=2, size=2><label for="m">:</label>
<input type="text" id="m" name="m", maxlength=2, size=2><label for="t"><br>Minutes:</label>
<input type="text" id="t" name="t", maxlength=2, size=2, value="5">
<br><br><input type="submit" value="Add"></form><br><br>'''
    return html
