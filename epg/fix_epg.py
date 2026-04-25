import requests
from lxml import etree
import os

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def main():
    # 下载原始 XML
    r = requests.get(SOURCE_URL, timeout=20)
    xml = r.content

    # 使用 recover + huge_tree 解析大文件
    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(xml, parser=parser)

    # ⭐ 不做任何时区转换
    # ⭐ 保留原始 start/stop（UTC +0000）
    # ⭐ IPTVnator 会自动转换到本地时间

    # 输出文件
    os.makedirs("epg", exist_ok=True)

    with open("epg/epg.xml", "wb") as f:
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True))

if __name__ == "__main__":
    main()
