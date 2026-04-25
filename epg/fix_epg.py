import requests
from datetime import datetime, timedelta
import re
import os
import pytz

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"
SOURCE_TZ = pytz.timezone("Asia/Shanghai")  # +0800

def get_local_offset():
    """自动检测 GitHub Runner 所在时区（UTC），并计算与中国时区的差值"""
    utc_now = datetime.now(pytz.utc)
    local_tz = pytz.timezone(os.getenv("TZ", "America/Toronto"))
    local_now = utc_now.astimezone(local_tz)
    offset_hours = int((local_now.utcoffset().total_seconds()) / 3600)
    return offset_hours, local_tz

def convert_time(match, offset_hours):
    """把 +0800 的时间转换成本地时区"""
    t = match.group(1)
    dt = datetime.strptime(t, "%Y%m%d%H%M%S")
    dt = SOURCE_TZ.localize(dt)

    # 转换到本地时区
    local_tz = pytz.timezone(os.getenv("TZ", "America/Toronto"))
    dt_local = dt.astimezone(local_tz)

    return dt_local.strftime("%Y%m%d%H%M%S") + f" {dt_local.strftime('%z')}"

def safe_download(url):
    """自动 fallback：源站挂了也不会导致 workflow 失败"""
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.text
        else:
            print("⚠️ 源站返回非 200 状态码，使用旧文件 fallback")
    except Exception as e:
        print("⚠️ 下载失败，使用旧文件 fallback:", e)

    # fallback：如果有旧文件，继续用旧的
    if os.path.exists("epg/epg.xml"):
        with open("epg/epg.xml", "r", encoding="utf-8") as f:
            return f.read()

    # fallback 失败：返回空字符串
    return ""

def main():
    offset_hours, local_tz = get_local_offset()
    print(f"本地时区: {local_tz}, 偏移: {offset_hours} 小时")

    xml = safe_download(SOURCE_URL)
    if not xml:
        print("❌ 无法获取 EPG 数据，退出")
        return

    # 替换 start/stop 时间
    xml = re.sub(r'start="(\d{14}) \+0800"', lambda m: f'start="{convert_time(m, offset_hours)}"', xml)
    xml = re.sub(r'stop="(\d{14}) \+0800"', lambda m: f'stop="{convert_time(m, offset_hours)}"', xml)

    # 输出到 epg/epg.xml
    os.makedirs("epg", exist_ok=True)
    with open("epg/epg.xml", "w", encoding="utf-8") as f:
        f.write(xml)

    print("✅ EPG 生成成功")

if __name__ == "__main__":
    main()
