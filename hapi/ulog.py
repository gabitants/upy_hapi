import os
import utime


CRITICAL = 40
NORMAL = 30
DEBUG = 20
LOG_LEVEL = 30
PRINT = True


def show(msg, level=NORMAL):
    global LOG_LEVEL, PRINT
    if LOG_LEVEL <= level:
        s = str(utime.time() % 86400)
        s = " " * (5 - len(s)) + f"{s} : {level} : {msg}"
        if PRINT:
            print(s)
        else:
            s += "\n"
            day = int(utime.time() / 86400)
            try:
                os.remove(f"{day - 2}.log")
            except OSError:
                pass
            except Exception as e:
                s += repr(e) + "\n"
            with open(f"{day}.log", "a") as f:
                f.write(s)
