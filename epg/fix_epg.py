import requests
from lxml import etree
import os
import random

# -----------------------------
#  EPG URLs
# -----------------------------
TW_URL = "https://epg.pw/xmltv/epg_TW.xml"
CA_URL = "https://epg.pw/xmltv/epg_CA.xml"
FR_URL = "https://epg.pw/xmltv/epg_FR.xml"

# -----------------------------
#  保留频道列表
# -----------------------------
KEEP_TW = {
    "539301",  # Discovery
    "456655",  # HBO HD
    "456656",  # HBO 強檔鉅獻
    "456657",  # HBO 原創鉅獻
    "456658",  # HBO 溫馨家庭
}

KEEP_CA = {
    "470483",  # BBC News (North America)
    "470859",  # CTV Toronto HD
    "470729",  # Global Toronto HD
    "470684",  # BNN Bloomberg HD (替换后的 ID)
}

KEEP_FR = {
    "444724",  # Eurosport 1
    "444725",  # Eurosport 2
    "55773",   # beIN SPORTS 1
    "443147",  # beIN SPORTS 2
    "54963",   # beIN SPORTS 3
}

# -----------------------------
#  FR 节目 ID 映射（解决 FR 节目丢失）
# -----------------------------
FR_MAP = {
    "444724": "444724",
    "eurosport1": "444724",
    "fr_444724": "444724",

    "444725": "444725",
    "eurosport2": "444725",
    "fr_444725": "444725",

    "55773": "55773",
    "beinsports1": "55773",

    "443147": "443147",
    "beinsports2": "443147",

    "54963": "54963",
    "beinsports3": "54963",
}

DELETE_RATIO_TW = 0.99  # TW 其他频道删 99%

# -----------------------------
#  时区修正
# -----------------------------
def fix_tw(t):
    return t[:-5] + "+0800" if t.endswith("+0000") else t

def fix_ca(t):
    return t[:-5] + "-0400" if t.endswith("+0000") else t

def fix_fr(t):
    return t[:-5] + "+0200" if t.endswith("+0000") else t

# -----------------------------
#  下载并解析 XML
# -----------------------------
def load_epg(url):
    r = requests.get(url, timeout=20)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    return etree.fromstring(r.content, parser=parser)

# -----------------------------
#  TW 过滤逻辑（保留频道不删，其他删 99%）
# -----------------------------
def process_tw(root):
    channels, programmes = [], []

    for ch in root.findall("channel"):
        channels.append(ch)

    for prog in root.findall("programme"):
        cid = prog.get("channel")

        if cid in KEEP_TW:
            programmes.append(prog)
        else:
            if random.random() > DELETE_RATIO_TW:
                programmes.append(prog)

    return channels, programmes

# -----------------------------
#  CA 过滤逻辑（保留频道完整保留，其他频道全部删除）
# -----------------------------
def process_ca(root):
    channels, programmes = [], []

    for ch in root.findall("channel"):
        cid = ch.get("id")

        # 替换 BNN Bloomberg ID
        if cid == "470787":
            ch.set("id", "470684")
            name = ch.find("display-name")
            if name is not None:
                name.text = "BNN Bloomberg HD"
            cid = "470684"

        if cid in KEEP_CA:
            channels.append(ch)

    for prog in root.findall("programme"):
        cid = prog.get("channel")

        if cid == "470787":
            prog.set("channel", "470684")
            cid = "470684"

        if cid in KEEP_CA:
            programmes.append(prog)

    return channels, programmes

# -----------------------------
#  FR 过滤逻辑（保留频道完整保留 + ID 映射修复）
# -----------------------------
def process_fr(root):
    channels, programmes = [], []

    # 频道
    for ch in root.findall("channel"):
        cid = ch.get("id")
        if cid in KEEP_FR:
            channels.append(ch)

    # 节目
    for prog in root.findall("programme"):
        cid = prog.get("channel")

        # 映射修正（关键）
        if cid in FR_MAP:
            new_id = FR_MAP[cid]
            prog.set("channel", new_id)
            cid = new_id

        if cid in KEEP_FR:
            programmes.append(prog)

    return channels, programmes

# -----------------------------
#  主流程
# -----------------------------
def main():
    print("开始处理 TW + CA + FR EPG ...")

    tw_root = load_epg(TW_URL)
    ca_root = load_epg(CA_URL)
    fr_root = load_epg(FR_URL)

    tw_channels, tw_programmes = process_tw(tw_root)
    ca_channels, ca_programmes = process_ca(ca_root)
    fr_channels, fr_programmes = process_fr(fr_root)

    final_root = etree.Element("tv")

    # 合并频道
    for ch in tw_channels + ca_channels + fr_channels:
        final_root.append(ch)

    # 合并节目 + 时区修正
    for prog in tw_programmes:
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_tw(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_tw(prog.attrib["stop"])
        final_root.append(prog)

    for prog in ca_programmes:
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_ca(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_ca(prog.attrib["stop"])
        final_root.append(prog)

    for prog in fr_programmes:
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_fr(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_fr(prog.attrib["stop"])
        final_root.append(prog)

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(final_root, encoding="utf-8", xml_declaration=True))

    print("完成：epg/epg.xml")

if __name__ == "__main__":
    main()
