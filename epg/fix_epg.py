import requests
from lxml import etree
from datetime import datetime, timedelta
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def subtract_8_hours(timestr):
    try:
        dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")
        dt_fixed = dt - timedelta(hours=8)
        return dt_fixed.strftime("%Y%m%d%H%M%S") + " +0000"
    except:
        return timestr

def main():
    print("正在获取原始数据并执行 -8 小时修正...")
    r = requests.get(SOURCE_URL, timeout=20)

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = subtract_8_hours(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = subtract_8_hours(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg.xml"   # ← 必须叫 epg.xml

    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    print(f"成功生成: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
