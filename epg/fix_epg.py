import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"
SOURCE_TZ = pytz.timezone("Asia/Shanghai")
LOCAL_TZ = pytz.timezone("America/Toronto")

def convert_time(timestr):
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S")
    dt = SOURCE_TZ.localize(dt)
    dt_local = dt.astimezone(LOCAL_TZ)
    return dt_local.strftime("%Y%m%d%H%M%S %z")

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    root = ET.fromstring(xml)

    for prog in root.findall("programme"):
        start = prog.get("start")
        stop = prog.get("stop")

        if start:
            prog.set("start", convert_time(start[:14]))
        if stop:
            prog.set("stop", convert_time(stop[:14]))

    os.makedirs("epg", exist_ok=True)
    ET.ElementTree(root).write("epg/epg.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
