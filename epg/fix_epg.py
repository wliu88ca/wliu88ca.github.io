import requests
from lxml import etree
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

def fix_timezone(timestr):
    # timestr 格式：YYYYMMDDHHMMSS +0000
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def main():
    print("正在获取原始 epg_TW.xml 并将时区从 +0000 改为 +0800 ...")
    r = requests.get(SOURCE_URL, timeout=20)

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 遍历所有 <programme>
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timezone(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timezone(prog.attrib["stop"])

    # 输出 epg.xml（workflow 需要这个文件名）
    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg.xml"

    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    print(f"成功生成: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
