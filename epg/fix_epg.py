import requests
from lxml import etree
import os
import random

EPG_URL = "https://epg.pw/xmltv/epg.xml"

KEEP = {
    "539301",
    "456655",
    "456656",
    "456657",
    "456658",
    "470483",
    "470859",
    "470729",
    "470684",
    "444724",
    "444725",
    "55773",
    "443147",
    "54963",
}

FR_MAP = {
    "eurosport1": "444724",
    "fr_444724": "444724",
    "444724": "444724",
    "eurosport2": "444725",
    "fr_444725": "444725",
    "444725": "444725",
    "beinsports1": "55773",
    "55773": "55773",
    "beinsports2": "443147",
    "443147": "443147",
    "beinsports3": "54963",
    "54963": "54963",
}

def detect_timezone(channel):
    name = channel.find("display-name")
    if name is None:
        return None

    lang = name.get("lang", "").upper()

    if lang == "FR":
        return "+0200"
    if lang == "ZH":
        return "+0800"
    if lang in ("EN", "CA"):
        return "-0400"

    return None

def fix_time(t, new_offset):
    if not t.endswith("+0000") and not t.endswith("-0000"):
        return t
    return t[:-5] + new_offset

def load_epg(url):
    r = requests.get(url, timeout=30)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    return etree.fromstring(r.content, parser=parser)

def main():
    print("加载官方 epg.xml ...")
    root = load_epg(EPG_URL)

    final_root = etree.Element("tv")
    channel_tz = {}

    for ch in root.findall("channel"):
        cid = ch.get("id")

        if cid == "470787":
            cid = "470684"
            ch.set("id", "470684")

        if cid in FR_MAP:
            new_id = FR_MAP[cid]
            ch.set("id", new_id)
            cid = new_id

        tz = detect_timezone(ch)
        if tz:
            channel_tz[cid] = tz

        if cid in KEEP:
            final_root.append(ch)

    for prog in root.findall("programme"):
        cid = prog.get("channel")

        if cid == "470787":
            cid = "470684"
            prog.set("channel", "470684")

        if cid in FR_MAP:
            new_id = FR_MAP[cid]
            prog.set("channel", new_id)
            cid = new_id

        if cid in KEEP:
            tz = channel_tz.get(cid)
            if tz:
                if "start" in prog.attrib:
                    prog.attrib["start"] = fix_time(prog.attrib["start"], tz)
                if "stop" in prog.attrib:
                    prog.attrib["stop"] = fix_time(prog.attrib["stop"], tz)
            final_root.append(prog)
            continue

        if random.random() < 0.001:
            tz = channel_tz.get(cid)
            if tz:
                if "start" in prog.attrib:
                    prog.attrib["start"] = fix_time(prog.attrib["start"], tz)
                if "stop" in prog.attrib:
                    prog.attrib["stop"] = fix_time(prog.attrib["stop"], tz)
            final_root.append(prog)

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(final_root, encoding="utf-8", xml_declaration=True))

    print("完成：epg/epg.xml")

if __name__ == "__main__":
    main()
