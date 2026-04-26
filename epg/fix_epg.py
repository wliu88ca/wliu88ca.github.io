import requests
from lxml import etree
import os
import random

TW_URL = "https://epg.pw/xmltv/epg_TW.xml"
CA_URL = "https://epg.pw/xmltv/epg_CA.xml"

# TW 保留频道
KEEP_TW = {
    "539301",  # Discovery
    "456655",  # HBO HD
    "456656",  # HBO 強檔鉅獻
    "456657",  # HBO 原創鉅獻
    "456658",  # HBO 溫馨家庭
}

# CA 保留频道（注意：BNN Bloomberg 改成 470684）
KEEP_CA = {
    "470483",  # BBC News (North America)
    "470859",  # CTV Toronto HD
    "470729",  # Global Toronto HD
    "470684",  # BNN Bloomberg HD
}

DELETE_RATIO = 0.99  # 删除 99% 节目

def fix_timezone_tw(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def fix_timezone_ca(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "-0400"
    return timestr

def load_epg(url):
    r = requests.get(url, timeout=20)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    return etree.fromstring(r.content, parser=parser)

def filter_epg(root, keep_ids, is_ca=False):
    new_channels = []
    new_programmes = []

    # 处理频道
    for ch in root.findall("channel"):
        cid = ch.get("id")

        # 替换 BNN Bloomberg ID
        if cid == "470787":
            ch.set("id", "470684")
            name = ch.find("display-name")
            if name is not None:
                name.text = "BNN Bloomberg HD"
            cid = "470684"

        new_channels.append(ch)

    # 处理节目
    for prog in root.findall("programme"):
        cid = prog.get("channel")

        # 替换节目里的 BNN Bloomberg ID
        if cid == "470787":
            prog.set("channel", "470684")
            cid = "470684"

        # ⭐ 保留频道 → 永远保留节目
        if cid in keep_ids:
            new_programmes.append(prog)
            continue

        # ⭐ 其他频道 → 删除 99%
        if random.random() > DELETE_RATIO:
            new_programmes.append(prog)

    return new_channels, new_programmes

def main():
    print("处理 TW + CA EPG，保留频道不参与删除，其他节目删除 99% ...")

    tw_root = load_epg(TW_URL)
    ca_root = load_epg(CA_URL)

    tw_channels, tw_programmes = filter_epg(tw_root, KEEP_TW)
    ca_channels, ca_programmes = filter_epg(ca_root, KEEP_CA, is_ca=True)

    final_root = etree.Element("tv")

    # 合并频道
    for ch in tw_channels + ca_channels:
        final_root.append(ch)

    # 合并节目 + 时区处理
    for prog in tw_programmes:
        prog.attrib["start"] = fix_timezone_tw(prog.attrib["start"])
        prog.attrib["stop"] = fix_timezone_tw(prog.attrib["stop"])
        final_root.append(prog)

    for prog in ca_programmes:
        prog.attrib["start"] = fix_timezone_ca(prog.attrib["start"])
        prog.attrib["stop"] = fix_timezone_ca(prog.attrib["stop"])
        final_root.append(prog)

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(final_root, encoding="utf-8", xml_declaration=True))

    print("完成: epg/epg.xml")

if __name__ == "__main__":
    main()
