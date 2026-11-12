#!/usr/bin/env python3
"""เครื่องมือแฟ้มงานของเลขา: เปิดแฟ้มงาน บันทึกเหตุการณ์ และสรุปสถานะ

ใช้งาน:
  python office.py init   JOB "ชื่องาน"
  python office.py log    JOB <ฝ่าย> <สถานะ> "ข้อความ"
  python office.py status JOB
  python office.py ev     JOB <ชนิด> [--team X | --teams A,B] [--to X] [--pct N] [--with A,B] [--title T] "ข้อความ"
  python office.py outbox JOB        # พิมพ์ writes สำหรับ ArtifactData batch แล้วล้างคิว
ชนิดเหตุการณ์ออฟฟิศสด: order, plan, assign, working, deliver, review_pass, review_fail, issue,
  meeting_start, meeting_say, meeting_end, handover, report, approval_request, approved, rejected,
  published, done, note
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


EVENT_TYPES = {"order", "plan", "assign", "working", "deliver", "review_pass", "review_fail", "issue",
               "meeting_start", "meeting_say", "meeting_end", "handover", "report", "approval_request",
               "approved", "rejected", "published", "done", "note"}
CODES = {"CEO", "SEC", "HEAD", "STR", "ARC", "MEP", "PUR", "PLN", "BOQ", "CNT", "TRN", "DEV", "WEB", "SKP"}


def _codes(s):
    out = [c.strip().upper() for c in s.split(",") if c.strip()]
    bad = [c for c in out if c not in CODES]
    if bad:
        sys.exit(f"ไม่รู้จักรหัส {', '.join(bad)} (ใช้ได้: {', '.join(sorted(CODES))})")
    return out


def ev(job: pathlib.Path, args):
    """เพิ่มเหตุการณ์หนึ่งรายการเข้าคิวส่งออฟฟิศสด (JOB/office_outbox.jsonl)"""
    import argparse
    ap = argparse.ArgumentParser(prog="office.py ev")
    ap.add_argument("type")
    ap.add_argument("msg")
    ap.add_argument("--team"); ap.add_argument("--teams"); ap.add_argument("--to")
    ap.add_argument("--pct", type=float); ap.add_argument("--with", dest="with_"); ap.add_argument("--title")
    a = ap.parse_args(args)
    if a.type not in EVENT_TYPES:
        sys.exit(f"ไม่รู้จักชนิด {a.type} (ใช้ได้: {', '.join(sorted(EVENT_TYPES))})")
    import time
    seq = int(time.time() * 1000)
    seq_file = job / ".office_seq"
    last = int(seq_file.read_text()) if seq_file.exists() else 0
    seq = max(seq, last + 1)
    seq_file.write_text(str(seq))
    jid = job.resolve().name
    doc = {"seq": seq, "t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "job": jid, "type": a.type, "msg": a.msg[:300]}
    if a.team: doc["team"] = _codes(a.team)[0]
    if a.teams: doc["teams"] = _codes(a.teams)
    if a.to: doc["to"] = _codes(a.to)[0]
    if a.pct is not None: doc["pct"] = max(0, min(100, a.pct))
    if a.with_: doc["with"] = _codes(a.with_)
    if a.title: doc["title"] = a.title[:120]
    write = {"op": "set", "collection": "events", "doc_id": f"{jid}-{seq}", "data": doc}
    with open(job / "office_outbox.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(write, ensure_ascii=False) + "\n")
    print(json.dumps(write, ensure_ascii=False))


def outbox(job: pathlib.Path):
    """พิมพ์ writes ที่ค้างในคิว (สูงสุด 50) เป็น JSON array สำหรับ ArtifactData action=batch แล้วล้างส่วนที่พิมพ์"""
    path = job / "office_outbox.jsonl"
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        print("[]")
        return
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    take, rest = lines[:50], lines[50:]
    print(json.dumps([json.loads(l) for l in take], ensure_ascii=False, indent=1))
    path.write_text("".join(l + "\n" for l in rest), encoding="utf-8")
    if rest:
        print(f"# ยังเหลือ {len(rest)} รายการ เรียก outbox อีกครั้ง", file=sys.stderr)


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
    elif cmd == "ev" and len(argv) >= 5:
        ev(job, argv[3:])
    elif cmd == "outbox":
        outbox(job)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
