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

# CA 保留频道
KEEP_CA = {
    "470483",  # BBC News (North America)
    "470859",  # CTV Toronto HD
    "470729",  # Global Toronto HD
    "470787",  # BNN Bloomberg
}

DELETE_RATIO = 0.99  # 删除 99% 节目

def fix_timezone(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def load_epg(url):
    r = requests.get(url, timeout=20)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    return etree.fromstring(r.content, parser=parser)

def filter_epg(root, keep_ids):
    new_channels = []
    new_programmes = []

    # 保留所有频道（频道本身不删）
    for ch in root.findall("channel"):
        new_channels.append(ch)

    # 节目过滤
    for prog in root.findall("programme"):
        ch = prog.get("channel")

        if ch in keep_ids:
            new_programmes.append(prog)
        else:
            if random.random() > DELETE_RATIO:
                new_programmes.append(prog)

    return new_channels, new_programmes

def main():
    print("处理 TW + CA EPG，保留指定频道，其他节目删除 99% ...")

    # 载入 TW + CA
    tw_root = load_epg(TW_URL)
    ca_root = load_epg(CA_URL)

    # 过滤 TW
    tw_channels, tw_programmes = filter_epg(tw_root, KEEP_TW)

    # 过滤 CA
    ca_channels, ca_programmes = filter_epg(ca_root, KEEP_CA)

    # 创建最终 <tv>
    final_root = etree.Element("tv")

    # 合并频道
    for ch in tw_channels + ca_channels:
        final_root.append(ch)

    # 合并节目
    for prog in tw_programmes + ca_programmes:
        # 改时区
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timezone(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timezone(prog.attrib["stop"])
        final_root.append(prog)

    # 输出 epg.xml
    os.makedirs("epg", exist_ok=True)
    output_file = "epg/epg.xml"

    with open(output_file, "wb") as f:
        f.write(etree.tostring(final_root, encoding="utf-8", xml_declaration=True))

    print(f"完成: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
