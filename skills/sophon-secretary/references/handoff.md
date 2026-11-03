# โครงแฟ้มงานและไฟล์ส่งต่องาน

```
JOB/
├── 00_order.md              คำสั่งของพี่โสภณ (เลขาเขียน)
├── 01_plan.json             แผนงาน + ใบสั่งงาน (หัวหน้าเขียน)
├── in/                      ไฟล์ต้นฉบับ: แบบ PDF/รูป, Spec, ราคาบริษัท, Vendor List, แบบฟอร์ม BOQ
├── teams/
│   ├── STR/  ARC/  MEP/     takeoff.json, backup.xlsx (ถ้าทำ), report.md
│   ├── PUR/                 prices.json, sources.md, report.md
│   ├── PLN/                 schedule.json, gantt/scurve (xlsx/png/html), report.md
│   └── BOQ/                 BOQ_<ชื่องาน>.xlsx, presentation (pptx/html/pdf), report.md
├── meetings/MTG-001.md      รายงานการประชุมแก้ปัญหา
├── reviews/wave-A.md        ผลตรวจของหัวหน้า
├── issues.md                ทะเบียนปัญหา (เลขาดูแล)
├── log.jsonl                บันทึกเหตุการณ์ (office.py log)
├── 90_head_summary.md       สรุปส่งมอบของหัวหน้า
└── 99_report_to_sophon.md   รายงานของเลขาถึงพี่โสภณ
```

## 01_plan.json (หัวหน้า)
```json
{
  "job": "บ้านพักอาศัย 2 ชั้น คุณ ก.",
  "scope": ["STR", "ARC", "MEP", "PUR", "PLN", "BOQ"],
  "sheets": {"STR": "PDF หน้า 12-20", "ARC": "PDF หน้า 1-11", "MEP": "PDF หน้า 21-30"},
  "standards": {"vat": "แยก VAT 7%", "factor_f": false, "currency": "THB", "waste": "ตาม SKILL/references/team-standards.md"},
  "waves": [
    {"id": "A", "teams": ["STR", "ARC", "MEP", "PLN"]},
    {"id": "B", "teams": ["PUR", "PLN"], "after": "A"},
    {"id": "C", "teams": ["BOQ"], "after": "B"}
  ],
  "orders": {
    "STR": {"wave": "A", "brief": "ข้อความใบสั่งงานพร้อมส่ง ...", "deliver": "teams/STR/takeoff.json + report.md", "due": "จบ wave A"},
    "PLN": {"wave": ["A", "B"], "brief_A": "...", "brief_B": "..."}
  },
  "assumptions": ["..."],
  "questions_for_sophon": []
}
```

## takeoff.json (STR / ARC / MEP)
1 รายการ BOQ = 1 item, ปริมาณมาจาก backup ทีละตำแหน่ง ย้อนกลับไปหาแบบได้
```json
{
  "team": "STR",
  "items": [
    {
      "id": "STR-02-001",
      "cat": "งานโครงสร้าง", "sub": "งานคอนกรีต",
      "desc": "คอนกรีตโครงสร้าง 240 ksc (Cylinder)",
      "unit": "ลบ.ม.",
      "price_key": "CONC-240",
      "spec_ref": "Spec ข้อ 3.2",
      "backup": [
        {"loc": "F1 กริด A-1..A-4", "page": "S-02", "n": 4, "expr": "1.2*1.2*0.4", "qty": 2.304},
        {"loc": "C1 ชั้น 1", "page": "S-03", "n": 8, "expr": "0.2*0.2*3.0", "qty": 0.96}
      ],
      "qty_net": 3.264, "waste_pct": 5, "qty": 3.43,
      "note": ""
    }
  ],
  "assumptions": ["..."],
  "issues": []
}
```
`issues[]` ใช้รูปแบบเดียวกันทุกฝ่าย:
```json
{"id": "STR-I01", "title": "ขนาดคาน B2 ในแปลนกับตารางคานไม่ตรงกัน",
 "detail": "แปลน S-03 ระบุ 0.20x0.40 ตาราง S-08 ระบุ 0.20x0.50",
 "impact": "คอนกรีต +0.6 ลบ.ม. / ระดับฝ้า ARC อาจต้องลด",
 "with": ["ARC", "MEP"], "need_meeting": "yes", "need_sophon": "no",
 "temp_assumption": "ใช้ 0.20x0.50 ตามตาราง (ปลอดภัยกว่า)"}
```

## prices.json (PUR)
```json
{
  "as_of": "2026-11-03",
  "prices": [
    {"price_key": "CONC-240", "desc": "คอนกรีตผสมเสร็จ 240 ksc", "unit": "ลบ.ม.",
     "material": 2350, "labour": 350,
     "source": "Vendor List / ราคาบริษัท / เว็บ", "vendor": "ชื่อร้าน", "url": "...", "tel": "...", "line": "...",
     "quotes": [2350, 2400, 2290], "confidence": "สูง/กลาง/ต่ำ", "note": "ราคารวมขนส่งในรัศมี 20 กม."}
  ],
  "missing": [],
  "issues": []
}
```

## schedule.json (PLN)
```json
{
  "start_date": "2026-12-01", "workdays_per_week": 6, "holidays": ["2026-12-31"],
  "activities": [
    {"id": "A10", "wbs": "1.2", "name": "ฐานราก", "dur": 10, "pred": ["A05FS"], "boq_ids": ["STR-02-*"], "crew": "ช่างปูน 6"}
  ],
  "critical_path": ["A05", "A10", "..."],
  "installments": [{"no": 1, "milestone": "งานฐานรากแล้วเสร็จ", "pct": 15}],
  "procurement_plan": [{"price_key": "STEEL-DB12", "order_by": "2026-12-05", "lead_days": 7}],
  "issues": []
}
```

## report.md (ทุกฝ่าย)
```markdown
# รายงาน <ฝ่าย>: <ชื่องาน>
## สิ่งที่ส่ง
## ตัวเลขสำคัญ
## สมมติฐาน
## ปัญหา   (คัดจาก issues[] — ระบุว่าแก้แล้วภายในฝ่าย / ต้องประชุมกับฝ่าย ... / ต้องให้พี่โสภณตัดสิน)
## ตรวจตัวเองแล้ว (checklist ของฝ่าย)
```

## issues.md (เลขา)
| # | วันที่ | ปัญหา | ผู้แจ้ง | ฝ่ายเกี่ยวข้อง | สถานะ | อ้างอิง |
|---|---|---|---|---|---|---|
| I-001 | 2026-11-03 | คาน B2 ขนาดไม่ตรงกัน | STR | ARC, MEP | แก้แล้ว (MTG-001) | meetings/MTG-001.md |

สถานะ: เปิด → นัดประชุม → แก้แล้ว (ภายในฝ่าย / MTG-xxx) → รอพี่โสภณตัดสิน → ปิด
