import requests
from lxml import etree
from datetime import datetime
import pytz
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def convert_utc_to_toronto(timestr):
    # 原始格式：YYYYMMDDHHMMSS +0000
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")

    # 转换到 Toronto
    toronto_tz = pytz.timezone("America/Toronto")
    dt_toronto = dt.astimezone(toronto_tz)

    # 输出格式：YYYYMMDDHHMMSS-0400
    return dt_toronto.strftime("%Y%m%d%H%M%S%z")

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(xml, parser=parser)

    # 遍历所有 <programme>，转换 start/stop
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = convert_utc_to_toronto(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = convert_utc_to_toronto(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
