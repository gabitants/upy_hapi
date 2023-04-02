import os
import utime
import hapi.ulog


def exists(path):
    """ If file exists. (bool) """
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def rlistdir(path=""):
    """ Recursive list of given dir. (list of str) """
    _l = []
    for _f in os.listdir(path):
        f = f"{path}/{_f}"
        if os.stat(f)[0] == 16384:
            _l.extend(rlistdir(f))
            continue
        _l.append(f)
    return _l


def json_read(path):
    """ Read JSON file. (dict)"""
    if not exists(path):
        return {}
    with open(path) as f:
        _d = eval(f.read())
    return _d


def json_write(path, content):
    """ Write JSON file. (None)"""
    with open(path, "w") as f:
        f.write(str(content))


def json_delete_key(path, key):
    """ Safe delete key from JSON file. (None)"""
    d = json_read(path)
    if key not in d:
        return
    del d[key]
    json_write(path, d)


def json_add_key(path, key, value):
    """ Safe add key and value to JSON file. (None)"""
    d = json_read(path)
    if key in d and d.get(key) == value:
        return
    d[key] = value
    json_write(path, d)


def wait(condition, period=2, timeout=15):
    """ Waits for a condition to become True. Period and timeout in seconds. (None) """
    start = utime.ticks_ms()  # get millisecond counter
    while not condition():
        utime.sleep(period)
        hapi.ulog.show("Waiting...")
        if utime.ticks_diff(utime.ticks_ms(), start) > timeout * 1000:
            hapi.ulog.show("Wait timeout!")
            return
    hapi.ulog.show("Wait concluded.")


def sync_ntp():
    """ Sync time through the internet. (None)"""
    try:
        from ntptime import settime
        settime()
        # localtime() gives (year, month, mday, hour, minute, second, weekday, yearday)
        hapi.ulog.show(f"Set time as {utime.localtime()}")
    except Exception as e:
        hapi.ulog.show(f"Failed do sync NTP: {e}")
