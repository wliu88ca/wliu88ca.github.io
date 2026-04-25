import requests
from lxml import etree
from datetime import datetime, timedelta
import pytz
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def convert_beijing_to_toronto(timestr):
    # 原始格式：YYYYMMDDHHMMSS +0000（但真实含义是北京时间）
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")

    # 第一步：把“假 UTC”当成北京时间（UTC+8）
    beijing_tz = pytz.timezone("Asia/Shanghai")
    dt_beijing = dt.replace(tzinfo=pytz.UTC).astimezone(beijing_tz)

    # 第二步：转换成 Toronto（UTC-4）
    toronto_tz = pytz.timezone("America/Toronto")
    dt_toronto = dt_beijing.astimezone(toronto_tz)

    # 输出格式：YYYYMMDDHHMMSS-0400
    return dt_toronto.strftime("%Y%m%d%H%M%S%z")

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(xml, parser=parser)

    # 遍历所有 <programme>，修正 start/stop
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = convert_beijing_to_toronto(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = convert_beijing_to_toronto(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
