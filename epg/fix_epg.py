import requests
from lxml import etree
from datetime import datetime, timedelta
import os
import time

SOURCE_URL = "https://epg.pw/xmltv/epg_CN.xml"

def fix_timestr(timestr, hours_to_subtract):
    """
    处理 EPG 时间戳。
    由于 epg.pw 返回的是 '20260426045000 +0000'，
    我们解析它，减去偏移量，然后以不带时区的格式返回，强迫播放器按系统当前时区显示。
    """
    try:
        # 解析原始格式
        dt = datetime.strptime(timestr, "%Y%m%d%H%M%S %z")
        
        # 减去偏移量 (根据你的实验，12 或 16)
        dt_fixed = dt - timedelta(hours=hours_to_subtract)
        
        # 返回格式：20260425125000（去掉时区后缀，让播放器不再乱跳）
        # 很多 IPTV 软件看到没有时区的字符串会直接取值
        return dt_fixed.strftime("%Y%m%d%H%M%S")
    except Exception:
        return timestr

def main():
    print(f"正在下载原始 EPG: {SOURCE_URL}...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"下载失败: {e}")
        return

    # 使用 huge_tree 处理大型 EPG 文件
    parser = etree.XMLParser(recover=True, huge_tree=True)
    root = etree.fromstring(r.content, parser=parser)

    # 技术派注意：这里建议根据你的观察微调，既然你要-12，我们就用12
    # 如果 12 还是快了，就改回 16
    HOURS_OFFSET = 12 

    print(f"正在批量修正时间戳 (偏移: -{HOURS_OFFSET}小时)...")
    for prog in root.findall("programme"):
        if "start" in prog.attrib:
            prog.attrib["start"] = fix_timestr(prog.attrib["start"], HOURS_OFFSET)
        if "stop" in prog.attrib:
            prog.attrib["stop"] = fix_timestr(prog.attrib["stop"], HOURS_OFFSET)

    # 导出目录
    os.makedirs("epg", exist_ok=True)
    
    # 技巧：在文件名里加个简易版本号，强迫 IPTVnator 识别为新文件
    file_version = time.strftime("%H%M")
    output_path = f"epg/epg_fixed_{file_version}.xml"

    with open(output_path, "wb") as f:
        # 使用 pretty_print 方便调试
        f.write(etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True))
    
    print(f"--- 修正成功 ---")
    print(f"本地文件路径: {os.path.abspath(output_path)}")
    print(f"请在 IPTVnator 中彻底删除旧 EPG，并导入此新文件。")

if __name__ == "__main__":
    main()
