import requests
from lxml import etree
from datetime import datetime, timedelta
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def subtract_8_hours(timestr):
    # 原始格式：YYYYMMDDHHMMSS +0000
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")

    # 减 8 小时（你验证的正确偏移）
    dt_fixed = dt - timedelta(hours=8)

    # 保持 +0000，不动 offset
    return dt_fixed.strftime("%Y%m%d%H%M%S") + " +0000"

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(xml, parser=parser)

    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = subtract_8_hours(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = subtract_8_hours(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
