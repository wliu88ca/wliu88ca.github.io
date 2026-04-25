import requests
from lxml import etree
from datetime import datetime, timedelta
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def subtract_12_hours(timestr):
    # 1. 解析原始格式：YYYYMMDDHHMMSS +0000
    try:
        dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")
        # 2. 精确减去 12 小时
        dt_fixed = dt - timedelta(hours=12)
        # 3. 返回不带时区的格式，强行对齐 IPTVnator 界面显示
        return dt_fixed.strftime("%Y%m%d%H%M%S")
    except:
        return timestr

def main():
    print("正在获取原始数据并执行 -12 小时修正...")
    r = requests.get(SOURCE_URL, timeout=20)
    
    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 遍历所有节目时间
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = subtract_12_hours(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = subtract_12_hours(prog.attrib["stop"])

    # 输出到本地目录
    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg_minus_12.xml"
    
    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))
    
    print(f"成功！请在 IPTVnator 中加载此文件: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
