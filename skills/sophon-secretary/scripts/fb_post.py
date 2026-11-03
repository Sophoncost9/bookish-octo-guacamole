#!/usr/bin/env python3
"""โพสต์ Facebook Page หลังพี่โสภณอนุมัติ (Graph API, ไม่ต้องติดตั้งไลบรารีเพิ่ม)

  python fb_post.py check   POST_DIR
  python fb_post.py approve POST_DIR --by "พี่โสภณ" [--now]
  python fb_post.py post    POST_DIR [--dry-run]

POST_DIR มี caption.txt, images/*.png|jpg (ไม่บังคับ), meta.json
env: FB_PAGE_ID, FB_PAGE_TOKEN, FB_GRAPH_VERSION (ค่าเริ่มต้น v23.0)
"""
import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

BKK = dt.timezone(dt.timedelta(hours=7))
IMG_EXT = {".png", ".jpg", ".jpeg"}


def load(post: pathlib.Path):
    cap_path = post / "caption.txt"
    if not cap_path.exists():
        sys.exit(f"ไม่พบ {cap_path}")
    caption = cap_path.read_text(encoding="utf-8").strip()
    meta = json.loads((post / "meta.json").read_text(encoding="utf-8")) if (post / "meta.json").exists() else {}
    img_dir = post / "images"
    images = sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMG_EXT) if img_dir.exists() else []
    return caption, meta, images


def parse_schedule(s):
    if not s:
        return None
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=BKK)


def fingerprint(caption, images, schedule):
    h = hashlib.sha256()
    h.update(caption.encode("utf-8"))
    h.update(b"\0" + (schedule or "NOW").encode())
    for p in images:
        h.update(b"\0" + p.name.encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def check(post, quiet=False):
    caption, meta, images = load(post)
    problems = []
    if not caption:
        problems.append("แคปชันว่าง")
    if len(caption) > 63000:
        problems.append("แคปชันยาวเกิน 63,000 ตัวอักษร")
    if len(images) > 10:
        problems.append("ภาพเกิน 10 ภาพ")
    for p in images:
        if p.stat().st_size > 10 * 1024 * 1024:
            problems.append(f"{p.name} ใหญ่เกิน 10 MB")
        try:
            from PIL import Image  # ไม่บังคับ
            w, h = Image.open(p).size
            if (w, h) not in {(1080, 1350), (1080, 1080), (2160, 2700), (2160, 2160)}:
                problems.append(f"{p.name} ขนาด {w}x{h} (แนะนำ 1080x1350 หรือ 1080x1080)")
        except ImportError:
            pass
    sched = parse_schedule(meta.get("schedule"))
    if sched:
        delta = sched - dt.datetime.now(BKK)
        if delta < dt.timedelta(minutes=10) or delta > dt.timedelta(days=30):
            problems.append(f"เวลาโพสต์ {meta['schedule']} ต้องอยู่ระหว่าง 10 นาทีถึง 30 วันจากตอนนี้ (หรือใช้ approve --now)")
    if not quiet:
        print(f"แคปชัน {len(caption)} ตัวอักษร | ภาพ {len(images)} | เวลาโพสต์ {meta.get('schedule') or 'ทันที'}")
        print("\n".join("  ⚠ " + x for x in problems) if problems else "  ✓ พร้อมเสนออนุมัติ")
    return problems


def approve(post, by, now):
    caption, meta, images = load(post)
    schedule = None if now else meta.get("schedule")
    rec = {
        "approved_by": by,
        "approved_at": dt.datetime.now(BKK).strftime("%Y-%m-%d %H:%M"),
        "schedule": schedule,
        "fingerprint": fingerprint(caption, images, schedule),
    }
    (post / "approval.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["status"] = "approved"
    (post / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"บันทึกการอนุมัติแล้ว: {by} | โพสต์ {schedule or 'ทันที'}")


def graph(path, fields, files=None):
    ver = os.environ.get("FB_GRAPH_VERSION", "v23.0")
    url = f"https://graph.facebook.com/{ver}/{path}"
    if files:
        boundary = uuid.uuid4().hex
        body = b""
        for k, v in fields.items():
            body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, p in files.items():
            ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{p.name}"\r\n'
                     f"Content-Type: {ctype}\r\n\r\n").encode() + p.read_bytes() + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    else:
        req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode())
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Facebook ตอบกลับข้อผิดพลาด {e.code}: {e.read().decode(errors='replace')}")


def post(post_dir, dry_run):
    caption, meta, images = load(post_dir)
    ap = post_dir / "approval.json"
    if not ap.exists():
        sys.exit("ยังไม่ได้รับอนุมัติจากพี่โสภณ — ห้ามโพสต์")
    approval = json.loads(ap.read_text(encoding="utf-8"))
    schedule = approval.get("schedule")
    if fingerprint(caption, images, schedule) != approval["fingerprint"]:
        sys.exit("เนื้อหา/ภาพ/เวลา เปลี่ยนหลังอนุมัติ — ต้องขออนุมัติพี่โสภณใหม่")
    if (post_dir / "result.json").exists():
        sys.exit("โพสต์นี้ถูกส่งไปแล้ว (มี result.json) — ไม่โพสต์ซ้ำ")
    problems = [p for p in check(post_dir, quiet=True) if not p.startswith("เวลาโพสต์") or schedule]
    if problems:
        sys.exit("ยังมีปัญหา: " + "; ".join(problems))

    sched_fields = {}
    if schedule:
        sched_fields = {"published": "false",
                        "scheduled_publish_time": str(int(parse_schedule(schedule).timestamp()))}
    plan = f"{'ตั้งเวลา ' + schedule if schedule else 'โพสต์ทันที'} | ภาพ {len(images)} | แคปชัน {len(caption)} ตัวอักษร"
    if dry_run:
        print("DRY RUN (ยังไม่ได้โพสต์จริง): " + plan)
        return

    page, token = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not page or not token:
        sys.exit("ไม่มี FB_PAGE_ID / FB_PAGE_TOKEN — ยังโพสต์อัตโนมัติไม่ได้ ส่งไฟล์ให้พี่โสภณโพสต์เอง")

    if len(images) == 1:
        res = graph(f"{page}/photos", {"caption": caption, "access_token": token, **sched_fields},
                    files={"source": images[0]})
    else:
        fields = {"message": caption, "access_token": token, **sched_fields}
        for i, p in enumerate(images):
            up = graph(f"{page}/photos", {"published": "false", "access_token": token}, files={"source": p})
            fields[f"attached_media[{i}]"] = json.dumps({"media_fbid": up["id"]})
        res = graph(f"{page}/feed", fields)

    pid = res.get("post_id") or res.get("id")
    result = {"post_id": pid, "url": f"https://www.facebook.com/{pid}" if pid else None,
              "mode": "scheduled" if schedule else "published", "schedule": schedule,
              "at": dt.datetime.now(BKK).strftime("%Y-%m-%d %H:%M"), "raw": res}
    (post_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["status"] = result["mode"]
    (post_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"สำเร็จ: {plan} | {result['url']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "approve", "post"])
    ap.add_argument("post_dir", type=pathlib.Path)
    ap.add_argument("--by")
    ap.add_argument("--now", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        sys.exit(1 if check(a.post_dir) else 0)
    if a.cmd == "approve":
        if not a.by:
            sys.exit("ต้องระบุ --by")
        approve(a.post_dir, a.by, a.now)
    else:
        post(a.post_dir, a.dry_run)


if __name__ == "__main__":
    main()
