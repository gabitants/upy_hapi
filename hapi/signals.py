# https://docs.micropython.org/en/v1.19.1/esp32/quickref.html#pins-and-gpio
from machine import Pin
pin = {
    # "P00": Pin(0, Pin.OUT),
    # "P01" Pins 1 and 3 are REPL UART TX and RX respectively
    # "P02": Pin(2, Pin.OUT),
    # "P03" Pins 1 and 3 are REPL UART TX and RX respectively
    # "P04": Pin(4, Pin.OUT),
    # "KS_In": Pin(5, Pin.IN, Pin.PULL_UP),
    # "P06" Pins 6, 7, 8, 11, 16, and 17 are used for connecting
    # "P07" the embedded flash, and are not recommended for other uses
    # "P08"
    # "P09": Pin(),  # UART1
    # "P10": Pin(),  # UART1
    # "P11"
    # "": Pin(12, Pin.IN, Pin.PULL_UP),
    # "": Pin(13, Pin.IN, Pin.PULL_UP),
    "B_Out": Pin(14, Pin.OUT, value=1),
    # "P15": Pin(15),
    # "P16"
    # "P17"
    # "V5_In": Pin(18, Pin.IN, Pin.PULL_UP),
    # "V4_In": Pin(19, Pin.IN, Pin.PULL_UP),
    # "V3_In": Pin(21, Pin.IN, Pin.PULL_UP),
    # "V2_In": Pin(22, Pin.IN, Pin.PULL_UP),
    # "V1_In": Pin(23, Pin.IN, Pin.PULL_UP),
    "V3_Out": Pin(25, Pin.OUT, value=1),
    "V2_Out": Pin(26, Pin.OUT, value=1),
    "V1_Out": Pin(27, Pin.OUT, value=1),
    # ADC1 : 32-39
    "V5_Out": Pin(32, Pin.OUT, value=1),
    "V4_Out": Pin(33, Pin.OUT, value=1),
    # Pins 34-39 are input only, and also do not have internal pull-up resistors
    # "P34": Pin(),
    # "P35": Pin(),
    # "P36": Pin(),
    # "P37": Pin(),
    # "P38": Pin(),
    # "P39": Pin(),
}
