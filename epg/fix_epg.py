import requests
from lxml import etree
import os
import random

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

# 你要保留的频道（节目全部保留）
KEEP_IDS = {
    "456641",  # BBC News
    "539301",  # Discovery
    "456655",  # HBO HD
    "456656",  # HBO 強檔鉅獻
    "456657",  # HBO 原創鉅獻
    "456658",  # HBO 溫馨家庭
    "539362",  # Bloomberg
}

DELETE_RATIO = 0.99   # 其他频道删掉 99% 节目

def fix_timezone(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def main():
    print("下载 epg_TW.xml，保留 7 个频道，其他频道删掉 95% 节目，并改时区为 +0800 ...")
    r = requests.get(SOURCE_URL, timeout=20)

    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 1. 不删频道本身（避免 IPTVnator 丢弃 EPG）
    #    频道越多越安全，只删节目即可

    # 2. 删除其他频道的 95% <programme>
    for prog in root.findall("programme"):
        ch = prog.get("channel")
        if ch not in KEEP_IDS:
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
