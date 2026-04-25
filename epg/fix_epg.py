import requests
from lxml import etree
from datetime import datetime
import pytz
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def fix_fake_utc_to_beijing(timestr):
    # 原始格式：YYYYMMDDHHMMSS +0000（真实含义是北京时间）
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")

    # 把“假 UTC”当成北京时间（UTC+8）
    beijing_tz = pytz.timezone("Asia/Shanghai")
    dt_beijing = dt.replace(tzinfo=pytz.UTC).astimezone(beijing_tz)

    # 输出格式：YYYYMMDDHHMMSS +0800（注意空格）
    return dt_beijing.strftime("%Y%m%d%H%M%S") + " +0800"

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(xml, parser=parser)

    # 遍历所有 <programme>，修正 start/stop
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_fake_utc_to_beijing(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_fake_utc_to_beijing(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
