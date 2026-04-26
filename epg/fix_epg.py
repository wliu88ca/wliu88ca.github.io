from pathlib import Path

src = Path("epg_TW.xml")      # 原始文件
dst = Path("epg.xml")         # 输出文件（只改时区）

text = src.read_text(encoding="utf-8")

# 只改时区标记，不动别的
text = text.replace(" +0000", " +0800")

dst.write_text(text, encoding="utf-8")
print("done: only timezone changed")
