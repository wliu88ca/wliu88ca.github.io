import requests
from lxml import etree
import os
import random

# -----------------------------
# 官方全量源
# -----------------------------
EPG_URL = "https://epg.pw/xmltv/epg.xml"

# -----------------------------
# 必须保留的频道
# -----------------------------
KEEP = {
    "539301",  # Discovery
    "456655",  # HBO HD
    "456656",  # HBO 強檔鉅獻
    "456657",  # HBO 原創鉅獻
    "456658",  # HBO 溫馨家庭

    "470483",  # BBC News (North America)
    "470859",  # CTV Toronto HD
    "470729",  # Global Toronto HD
    "470684",  # BNN Bloomberg HD

    "444724",  # Eurosport 1
    "444725",  # Eurosport 2
    "55773",   # beIN SPORTS 1
    "443147",  # beIN SPORTS 2
    "54963",   # beIN SPORTS 3
}

# -----------------------------
# FR 映射（必须保留）
# -----------------------------
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

# -----------------------------
# 时区规则（按频道语言）
# -----------------------------
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
