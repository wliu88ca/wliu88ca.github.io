import requests
from lxml import etree
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

def fix_timezone(timestr):
    if timestr.endswith("+0000"):
        return timestr[:-5] + "+0800"
    return timestr

def main():
    r = requests.get(SOURCE_URL, timeout=20)
    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 1. 删掉 <channel id="370137">
    for ch in root.findall("channel"):
        if ch.get("id") == "370137":
            root.remove(ch)
            break

    # 2. 删掉所有 <programme channel="370137">
    to_delete = [prog for prog in root.findall("programme") if prog.get("channel") == "370137"]
    for prog in to_delete:
        root.remove(prog)

    # 3. 改时区
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timezone(prog.attrib["start"])
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timezone(prog.attrib["stop"])

    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
