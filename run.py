from machine import WDT
import hapi
ws = hapi.WebServer("Hapi", "coqueiros")
# enable the WDT with a timeout of 5s (1s is the minimum)
wdt = WDT(timeout=25000)

if hapi.utils.exists("/lib/mcron"):
    import hapi.schedule


while True:
    ws.accept(hapi.html_gen.get_page)
    wdt.feed()
