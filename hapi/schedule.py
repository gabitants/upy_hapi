from hapi import signals
import hapi.ulog
import hapi.utils
import mcron

# https://github.com/fizista/micropython-mcron
mcron.init_timer()
hapi.ulog.show("MCRON started.")
SCHEDULE_FILE = "SCHEDULE"
SCHEDULE_ENABLED = True


def valve(i, value=None):
    """ Opens valve 'i' when value is True. Return valve value. (bool) """
    # Relay logic is inverted, so on is off and off is on.
    if value is True:
        signals.pin[f'V{i}_Out'].off()
    elif value is False:
        signals.pin[f'V{i}_Out'].on()
    return not signals.pin[f'V{i}_Out'].value()


def _start_pump(callback_id, *_):
    mcron.remove(callback_id)
    if not signals.pin['B_Out'].value():
        return
    if not any(valve(i + 1) for i in range(5)):
        hapi.ulog.show("Tried to start pump, but no valve is open!", level=hapi.ulog.CRITICAL)
        return
    hapi.ulog.show("Starting pump")
    signals.pin['B_Out'].off()


def pump(current_time, value):
    if value:
        if 'start_pump' in mcron.callback_table:
            return
        mcron.insert(current_time + 3, {0}, 'start_pump', _start_pump)
    else:
        hapi.ulog.show("Stopping pump")
        signals.pin['B_Out'].on()


def start_valve(current_time, i):
    global SCHEDULE_ENABLED
    if not SCHEDULE_ENABLED:
        hapi.ulog.show(f'Schedule control disabled, wont open V{i}')
        return
    if valve(i):
        return
    hapi.ulog.show(f'Opening V{i}')
    valve(i, True)
    pump(current_time, True)


def stop_valve(current_time, i):
    valves_open = sum(valve(i + 1) for i in range(5))
    if valves_open == 1:
        pump(current_time, False)

    def _close_valve(callback_id, *_):
        mcron.remove(callback_id)
        hapi.ulog.show(f"Closing V{i}")
        valve(i, False)

    callback_name = f'Stop_V{i}'
    if callback_name in mcron.callback_table:
        hapi.ulog.show(f"Routine '{callback_name}' already scheduled!", level=hapi.ulog.CRITICAL)
    else:
        mcron.insert(current_time + 3, {0}, callback_name, _close_valve)


def step_valve(current_time, i, t):
    start_valve(current_time, i)

    def _stop_valve(_callback_id, _current_time, _):
        mcron.remove(_callback_id)
        stop_valve(_current_time, i)

    callback_name = f'Step_V{i}_Stopper'
    if callback_name in mcron.callback_table:
        hapi.ulog.show(f"Routine '{callback_name}' already scheduled!", level=hapi.ulog.CRITICAL)
    else:
        mcron.insert(current_time + int(t) * 60, {0}, callback_name, _stop_valve)


def add_schedule(i, h, m, t):
    name = f'Step_V{i}_{h}_{m}'
    if name in mcron.callback_table:
        return
    hapi.ulog.show(f"Adding schedule {name} with {t} min")
    hapi.utils.json_add_key(SCHEDULE_FILE, name, t)

    def schedule_wrapper(callback_id, current_time, _):
        hapi.ulog.show(f"Cycling {callback_id}")
        step_valve(current_time, i, t)

    mcron.insert(mcron.PERIOD_DAY, {(int(h) + 3) * 60 * 60 + int(m) * 60}, name, schedule_wrapper)
    hapi.ulog.show(f"Schedule table: {mcron.timer_table}", level=hapi.ulog.DEBUG)


try:
    for k, _t in hapi.utils.json_read(SCHEDULE_FILE).items():
        info = [int(i) for i in k[6:].split("_")]
        info.append(_t)
        add_schedule(*info)
except Exception as e:
    hapi.ulog.show(e)
