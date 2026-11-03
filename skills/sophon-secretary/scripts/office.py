#!/usr/bin/env python3
"""เครื่องมือแฟ้มงานของเลขา: เปิดแฟ้มงาน บันทึกเหตุการณ์ และสรุปสถานะ

ใช้งาน:
  python office.py init   JOB "ชื่องาน"
  python office.py log    JOB <ฝ่าย> <สถานะ> "ข้อความ"
  python office.py status JOB
สถานะที่ใช้: assigned, working, delivered, review_pass, review_fail, issue, meeting, resolved, reported,
           awaiting_approval, approved, published, rejected
"""
import datetime as dt
import json
import pathlib
import sys

TEAMS = {
    "HEAD": "หัวหน้าทีม",
    "STR": "วิศวกรโครงสร้าง",
    "ARC": "วิศวกรถอดแบบสถาปัตย์",
    "MEP": "วิศวกรถอดแบบงานระบบ",
    "PUR": "ฝ่ายจัดซื้อ",
    "PLN": "ทีมวางแผนงานก่อสร้าง",
    "BOQ": "ทีม BOQ และ Presentation",
    "CNT": "ทีม Content AI",
    "TRN": "ทีมเนื้อหาการอบรม",
    "DEV": "ทีมเขียนโปรแกรม",
    "SEC": "เลขา",
}
STATUS_TH = {
    "assigned": "ได้รับมอบหมาย",
    "working": "กำลังทำ",
    "delivered": "ส่งงานแล้ว รอตรวจ",
    "review_pass": "หัวหน้าตรวจผ่าน",
    "review_fail": "หัวหน้าส่งกลับแก้",
    "issue": "พบปัญหา",
    "meeting": "กำลังประชุมแก้ปัญหา",
    "resolved": "แก้ปัญหาแล้ว",
    "reported": "รายงานพี่โสภณแล้ว",
    "awaiting_approval": "รอพี่โสภณตรวจ/อนุมัติ",
    "approved": "พี่โสภณอนุมัติแล้ว",
    "published": "โพสต์/เผยแพร่แล้ว",
    "rejected": "พี่โสภณไม่อนุมัติ",
}


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")


def init(job: pathlib.Path, name: str):
    for sub in ["in", "meetings", "reviews", "content", "training", "dev"] + [f"teams/{t}" for t in ["STR", "ARC", "MEP", "PUR", "PLN", "BOQ"]]:
        (job / sub).mkdir(parents=True, exist_ok=True)
    order = job / "00_order.md"
    if not order.exists():
        order.write_text(
            f"# คำสั่งงาน: {name}\n- รับคำสั่ง: {now()}  จาก: พี่โสภณ\n- งานที่สั่ง: \n- ไฟล์ต้นฉบับ: in/\n"
            "- ผลงานที่ต้องการ: \n- กำหนดส่ง: \n- ค่าที่ใช้แทนเพราะไม่ได้ระบุ: \n\n## คำสั่งเพิ่มเติม\n",
            encoding="utf-8",
        )
    issues = job / "issues.md"
    if not issues.exists():
        issues.write_text(
            "# ทะเบียนปัญหา\n\n| # | วันที่ | ปัญหา | ผู้แจ้ง | ฝ่ายเกี่ยวข้อง | สถานะ | อ้างอิง |\n"
            "|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    log(job, "SEC", "assigned", f"เปิดแฟ้มงาน: {name}")
    print(f"เปิดแฟ้มงานแล้ว: {job.resolve()}")


def log(job: pathlib.Path, team: str, status: str, msg: str):
    team = team.upper()
    if team not in TEAMS:
        sys.exit(f"ไม่รู้จักฝ่าย {team} (ใช้ได้: {', '.join(TEAMS)})")
    if status not in STATUS_TH:
        sys.exit(f"ไม่รู้จักสถานะ {status} (ใช้ได้: {', '.join(STATUS_TH)})")
    job.mkdir(parents=True, exist_ok=True)
    rec = {"t": now(), "team": team, "status": status, "msg": msg}
    with open(job / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def status(job: pathlib.Path):
    path = job / "log.jsonl"
    if not path.exists():
        sys.exit("ยังไม่มีบันทึกเหตุการณ์ — เปิดแฟ้มงานด้วย init ก่อน")
    last = {}
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            last[r["team"]] = r
            events.append(r)
    print(f"สถานะงาน ({now()})")
    for code, name in TEAMS.items():
        if code in last:
            r = last[code]
            print(f"  {name:<26} {STATUS_TH[r['status']]:<24} {r['t']}  {r['msg']}")
    open_issues = 0
    issues = job / "issues.md"
    if issues.exists():
        for row in issues.read_text(encoding="utf-8").splitlines():
            if row.startswith("| I-") and ("เปิด" in row or "นัดประชุม" in row or "รอพี่โสภณ" in row):
                open_issues += 1
    meetings = sorted((job / "meetings").glob("MTG-*.md")) if (job / "meetings").exists() else []
    print(f"ปัญหาที่ยังไม่ปิด: {open_issues} | การประชุมทั้งหมด: {len(meetings)}")
    print("เหตุการณ์ล่าสุด:")
    for r in events[-5:]:
        print(f"  {r['t']} [{TEAMS[r['team']]}] {STATUS_TH[r['status']]} — {r['msg']}")


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd, job = argv[1], pathlib.Path(argv[2])
    if cmd == "init":
        init(job, argv[3] if len(argv) > 3 else job.name)
    elif cmd == "log" and len(argv) >= 6:
        log(job, argv[3], argv[4], " ".join(argv[5:]))
    elif cmd == "status":
        status(job)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
