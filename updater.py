import urllib.request
import json
import re
from datetime import datetime
import zoneinfo

# รายการรหัสสาขาและข้อมูลที่ต้องการติดตาม
PROGRAMS = [
    {"id": "10010111110101A", "name": "หลักสูตรแพทยศาสตรบัณฑิต", "faculty": "คณะแพทยศาสตร์", "university": "จุฬาลงกรณ์มหาวิทยาลัย", "abbr": "CU", "category": "med", "quota": 300},
    {"id": "10010121110101A", "name": "วิศวกรรมคอมพิวเตอร์และดิจิทัล (CEDT)", "faculty": "คณะวิศวกรรมศาสตร์", "university": "จุฬาลงกรณ์มหาวิทยาลัย", "abbr": "CU", "category": "comp", "quota": 110},
    {"id": "10020115110101A", "name": "นิติศาสตรบัณฑิต (ศูนย์รังสิตและลำปาง)", "faculty": "คณะนิติศาสตร์", "university": "มหาวิทยาลัยธรรมศาสตร์", "abbr": "TU", "category": "law", "quota": 350},
    {"id": "10020116110101A", "name": "การบัญชีและบริหารธุรกิจ (BBA / ปกติ)", "faculty": "คณะพาณิชยศาสตร์และการบัญชี", "university": "มหาวิทยาลัยธรรมศาสตร์", "abbr": "TU", "category": "biz", "quota": 360},
    {"id": "10030118110101A", "name": "หลักสูตรพยาบาลศาสตรบัณฑิต (ศิริราช)", "faculty": "คณะพยาบาลศาสตร์", "university": "มหาวิทยาลัยมหิดล", "abbr": "MU", "category": "med", "quota": 305},
    {"id": "10050122110101A", "name": "วิทยาการคอมพิวเตอร์ (Computer Science)", "faculty": "คณะวิทยาศาสตร์", "university": "มหาวิทยาลัยเกษตรศาสตร์", "abbr": "KU", "category": "comp", "quota": 72},
    {"id": "10010138113101A", "name": "จิตวิทยา (สาขาวิชาจิตวิทยา)", "faculty": "คณะจิตวิทยา", "university": "จุฬาลงกรณ์มหาวิทยาลัย", "abbr": "CU", "category": "human", "quota": 100},
    {"id": "10040117110101A", "name": "เศรษฐศาสตรบัณฑิต (ภาคปกติ)", "faculty": "คณะเศรษฐศาสตร์", "university": "มหาวิทยาลัยเชียงใหม่", "abbr": "CMU", "category": "econ", "quota": 180},
    {"id": "10060126110101A", "name": "ทันตแพทยศาสตรบัณฑิต", "faculty": "คณะทันตแพทยศาสตร์", "university": "มหาวิทยาลัยขอนแก่น", "abbr": "KKU", "category": "med", "quota": 80},
    {"id": "10090124110101A", "name": "วิทยาการข้อมูลและการวิเคราะห์เชิงธุรกิจ", "faculty": "คณะเทคโนโลยีสารสนเทศ", "university": "สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง", "abbr": "KMITL", "category": "comp", "quota": 60},
    {"id": "10070125110101A", "name": "เภสัชศาสตรบัณฑิต (การบริบาลทางเภสัชกรรม)", "faculty": "คณะเภสัชศาสตร์", "university": "มหาวิทยาลัยสงขลานครินทร์", "abbr": "PSU", "category": "med", "quota": 95},
    {"id": "10070119110101A", "name": "เศรษฐศาสตร์และบริหารธุรกิจ", "faculty": "คณะเศรษฐศาสตร์", "university": "มหาวิทยาลัยสงขลานครินทร์", "abbr": "PSU", "category": "econ", "quota": 140}
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'th,en-US;q=0.7,en;q=0.3'
}

updated_data = []
print("🚀 กำลังดึงยอดวิวจริงจาก Next.js Payload ของ myTCAS...")

for item in PROGRAMS:
    pid = item["id"]
    url = f"https://course.mytcas.com/programs/{pid}"
    views = 0
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # วิธีที่ 1: ดึงจาก Next.js __NEXT_DATA__ JSON ภายในหน้า
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if next_data_match:
                try:
                    payload = json.loads(next_data_match.group(1))
                    page_props = payload.get("props", {}).get("pageProps", {})
                    # myTCAS มักเก็บไว้ใน program หรือ data
                    program_data = page_props.get("program") or page_props.get("data") or page_props
                    if isinstance(program_data, dict):
                        views = program_data.get("views") or program_data.get("view_count") or program_data.get("viewCount") or 0
                except Exception:
                    pass

            # วิธีที่ 2: หากวิธีที่ 1 ไม่พบ ให้ค้นหาคีย์ regex ใน JSON โดยตรง
            if not views:
                json_view_match = re.search(r'"view(?:s|_count|Count)"\s*:\s*(\d+)', html)
                if json_view_match:
                    views = int(json_view_match.group(1))

            # วิธีที่ 3: ดักจับจากข้อความภาษาไทยธรรมดา
            if not views:
                text_match = re.search(r"ยอดผู้เข้าชม\s*([\d,]+)\s*ครั้ง", html)
                if text_match:
                    views = int(text_match.group(1).replace(",", ""))

            print(f"✅ [{item['abbr']}] {item['name']}: {views:,} วิว")

    except Exception as e:
        print(f"⚠️ ดึงไม่สำเร็จ {pid}: {e}")

    item["views"] = views
    updated_data.append(item)

# วันเวลาปัจจุบันของประเทศไทย (UTC+7)
bkk_tz = zoneinfo.ZoneInfo("Asia/Bangkok")
now_str = datetime.now(bkk_tz).strftime("%Y-%m-%d %H:%M:%S")

output = {
    "last_sync": now_str,
    "programs": updated_data
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎉 บันทึกไฟล์ data.json สำเร็จ ณ เวลา {now_str}")
