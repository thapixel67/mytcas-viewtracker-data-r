import json
import re
from datetime import datetime
import zoneinfo
from playwright.sync_api import sync_playwright

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

updated_data = []

with sync_playwright() as p:
    # เปิด Chrome เลียนแบบผู้ใช้งานจริง
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for item in PROGRAMS:
        pid = item["id"]
        url = f"https://course.mytcas.com/programs/{pid}"
        views = 0
        try:
            # เปิดหน้าเว็บและรอให้หน้าโหลดเสร็จสมบูรณ์
            page.goto(url, wait_until="networkidle", timeout=25000)
            page.wait_for_timeout(1500) # รอ 1.5 วินาทีให้ตัวเลขเรนเดอร์

            # ดึงข้อความทั้งหมดที่ปรากฏบนหน้าจอจริง
            body_text = page.inner_text("body")
            
            # เจาะจงหาประโยคภาษาไทยตรงๆ: "ยอดผู้เข้าชม [ตัวเลข] ครั้ง"
            match = re.search(r"ยอดผู้เข้าชม\s*([\d,]+)\s*ครั้ง", body_text)
            if match:
                views = int(match.group(1).replace(",", ""))
                print(f"✅ [{item['abbr']}] {item['name']}: {views:,} วิว")
            else:
                print(f"⚠️ ไม่พบข้อความยอดวิวในหน้า: {item['name']}")

        except Exception as e:
            print(f"❌ โหลดไม่สำเร็จ {pid}: {e}")

        # อัปเดตยอดวิว (ถ้าดึงได้มากกว่า 0 ให้ใช้ค่านั้น)
        if views > 0:
            item["views"] = views
        updated_data.append(item)

    browser.close()

# บันทึกเวลาประเทศไทย
bkk_tz = zoneinfo.ZoneInfo("Asia/Bangkok")
now_str = datetime.now(bkk_tz).strftime("%Y-%m-%d %H:%M:%S")

output = {
    "last_sync": now_str,
    "programs": updated_data
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎉 อัปเดตข้อมูลสำเร็จ ณ เวลา {now_str}")
