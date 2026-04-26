import requests
from lxml import etree
import os
import random

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

KEEP_ID = "456657"   # 只保留这个频道的所有节目
DELETE_RATIO = 0.5   # 其他频道删掉 50%

def fix_timezone(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def main():
    print("下载 epg_TW.xml，保留 456657，其他频道随机删掉 50% 节目，并改时区为 +0800 ...")
    r = requests.get(SOURCE_URL, timeout=20)

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 1. 删除所有不是 KEEP_ID 的 <channel>（可选）
    #    你说“其他随便删掉 50%”，频道本身删不删都行
    #    我这里保留频道，但你要删我也能改
    #    先保留频道更安全（IPTVnator 更不容易丢弃 EPG）
    #    所以这里不删频道

    # 2. 删除其他频道的 50% <programme>
    for prog in root.findall("programme"):
        ch = prog.get("channel")
        if ch != KEEP_ID:
            if random.random() < DELETE_RATIO:
                root.remove(prog)

    # 3. 改时区
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timezone(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timezone(prog.attrib["stop"])

    # 4. 输出 epg.xml
    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg.xml"

    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    print(f"完成: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
