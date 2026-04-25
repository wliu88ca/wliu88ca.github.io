import requests
from datetime import datetime, timedelta
import re

URL = "https://epg.pw/xmltv/epg_CN.xml"

def convert_time(match):
    t = match.group(1)
    dt = datetime.strptime(t, "%Y%m%d%H%M%S")
    dt = dt - timedelta(hours=12)  # +0800 → -0400
    return dt.strftime("%Y%m%d%H%M%S") + " -0400"

xml = requests.get(URL).text

xml = re.sub(r'start="(\d{14}) \+0800"', lambda m: f'start="{convert_time(m)}"', xml)
xml = re.sub(r'stop="(\d{14}) \+0800"', lambda m: f'stop="{convert_time(m)}"', xml)

with open("epg.xml", "w", encoding="utf-8") as f:
    f.write(xml)
