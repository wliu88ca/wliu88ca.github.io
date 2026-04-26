import requests
from lxml import etree
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

# 你要保留的频道 ID（必须和 EPG 的 channel id 完全一致）
KEEP_IDS = {
    "Discovery",
    "HBO HD",
    "HBO 強檔鉅獻",
    "HBO 溫馨家庭",
    "HBO 原創鉅獻"
}

def fix_timezone(timestr):
    # 只改 +0000 → +0800，不动时间
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def main():
    print("正在获取 epg_TW.xml 并过滤频道...")

    r = requests.get(SOURCE_URL, timeout=20)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 1. 删除不在 KEEP_IDS 的 <channel>
    for ch in root.findall("channel"):
        if ch.attrib.get("id") not in KEEP_IDS:
            root.remove(ch)

    # 2. 删除不在 KEEP_IDS 的 <programme>
    for prog in root.findall("programme"):
        if prog.attrib.get("channel") not in KEEP_IDS:
            root.remove(prog)
            continue

        # 3. 修改时区
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timezone(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timezone(prog.attrib["stop"])

    # 输出 epg.xml（workflow 需要这个文件名）
    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg.xml"

    with open(output_file, "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

    print("成功生成:", os.path.abspath(output_file))

if __name__ == "__main__":
    main()
