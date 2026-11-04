#!/usr/bin/env python3
"""PHISO Shop Drawing — isolated (spread) footing generator.

Reads a footing config JSON (see examples/F1.json), computes every bar's
shape, dimensions, cut length, positions and weights, then writes:
  <out>/index.html                  interactive shop drawing + BBS + cutting plan + 3D
  <out>/<NAME>-bar-cutting-list.xlsx Excel BBS for the bar cutters (formulas live)
  <out>/<NAME>-calc.json            all computed numbers (for checking / reuse)

Usage: python3 build_footing.py config.json --out OUTDIR
All lengths in mm.
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "footing_template.html")


def ceil10(x):
    return int(math.ceil(x / 10.0) * 10)


def kgm(d):
    # unit weight kg/m = 0.00617 d^2 ; use Thai table values where common
    table = {6: 0.222, 9: 0.499, 10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853, 28: 4.834}
    return table.get(d, round(0.00617 * d * d, 3))


def name(t, d):
    return f"{t}{d}"


def compute(cfg):
    F = cfg["footing"]; Bx, By, t, depth = F["B"], F["L"], F["t"], F["depth"]
    c = cfg.get("cover", 50)
    stock = cfg.get("stock", 10000)
    grade = cfg.get("grade", {"DB": "SD40", "RB": "SR24"})
    assumed_grade = cfg.get("grade_assumed", True)
    warn = []
    bars = []
    bx, by = cfg["bars"]["x"], cfg["bars"]["y"]
    d1, d2 = bx["dia"], by["dia"]
    edge = cfg.get("first_bar_from_edge", c + 25)

    # ---- B1 : bottom layer along X (length Bx), spread across Y
    A1 = t - 2 * c                       # hook leg outer, up to top cover
    if A1 < 12 * d1:
        warn.append(f"ขางอ B1 = {A1} มม. น้อยกว่า 12d ({12*d1}) — ฐานบางเกินไป ตรวจสอบ")
    L1 = Bx - 2 * c
    cut1 = ceil10(2 * A1 + L1 - 2 * 2 * d1)
    posY = [(-(By / 2 - edge) + i * (By - 2 * edge) / (bx["n"] - 1)) if bx["n"] > 1 else 0 for i in range(bx["n"])]
    sp1 = (By - 2 * edge) / max(1, bx["n"] - 1)
    bars.append(dict(m="B1", t=bx["type"], d=d1, n=bx["n"], shape="U", dims={"A": A1, "B": L1, "C": A1}, cut=cut1,
                     c="--b1", desc=f"เหล็กล่างชั้นที่ 1 แนว X @{sp1/1000:.3f} ม.", pos=posY,
                     z=c + d1 / 2, top=t - c))
    # ---- B2 : second layer along Y, sits on B1
    A2 = A1 - d1
    L2 = By - 2 * c
    cut2 = ceil10(2 * A2 + L2 - 2 * 2 * d2)
    posX = [(-(Bx / 2 - edge) + i * (Bx - 2 * edge) / (by["n"] - 1)) if by["n"] > 1 else 0 for i in range(by["n"])]
    sp2 = (Bx - 2 * edge) / max(1, by["n"] - 1)
    bars.append(dict(m="B2", t=by["type"], d=d2, n=by["n"], shape="U", dims={"A": A2, "B": L2, "C": A2}, cut=cut2,
                     c="--b2", desc=f"เหล็กล่างชั้นที่ 2 แนว Y @{sp2/1000:.3f} ม. วางบน B1", pos=posX,
                     z=c + d1 + d2 / 2, top=t - c))
    for b, s in ((bars[0], sp1), (bars[1], sp2)):
        if s > 300:
            warn.append(f"{b['m']} ระยะเรียง {s:.0f} มม. เกิน 300 มม. — ตรวจสอบกับแบบ")

    # ---- R1 : perimeter tie ring (optional)
    ring = cfg["bars"].get("ring")
    if ring:
        dr = ring["dia"]; lap = ring.get("lap", 40 * dr)
        dmax = max(d1, d2)
        rx = int((Bx - 2 * c - 2 * dmax - 6) // 10 * 10)
        ry = int((By - 2 * c - 2 * dmax - 6) // 10 * 10)
        zr = ring.get("z", t - c - 20)
        cutr = ceil10(2 * (rx - dr) + 2 * (ry - dr) + lap)
        bars.append(dict(m="R1", t=ring["type"], d=dr, n=ring.get("n", 1), shape="O", dims={"A": rx, "B": ry, "L": lap},
                         cut=cutr, c="--ring", desc=f"เหล็กรัดรอบ วางในขาตั้ง B1/B2 ที่ +{zr/1000:.2f}", z=zr))

    # ---- Column starter bars + ties
    col = cfg.get("column")
    if col:
        cb, ch, cc = col["b"], col["h"], col.get("cover", 25)
        mn, tie = col["main"], col["tie"]
        dm, dt = mn["dia"], tie["dia"]
        above = col.get("above_ground", 40 * dm + 20)
        foot = col.get("foot", max(250, 12 * dm))
        zb = c + d1 + d2 + dm / 2              # bar seated on mesh
        Av = ceil10(depth + above - (zb - dm / 2))
        cutc = ceil10(Av + foot - 2 * dm)
        ox = cb / 2 - cc - dt - dm / 2
        oy = ch / 2 - cc - dt - dm / 2
        pts = [(sx * ox, sy * oy) for sx in (-1, 1) for sy in (-1, 1)]
        if mn["n"] >= 6:
            pts += [(0, -oy), (0, oy)]
        if mn["n"] >= 8:
            pts += [(-ox, 0), (ox, 0)]
        pts = pts[:mn["n"]]
        asm = col.get("assumed", False)
        bars.append(dict(m="C1", t=mn["type"], d=dm, n=mn["n"], shape="L", dims={"A": Av, "B": foot}, cut=cutc, c="--dw",
                         desc="เหล็กยืนเสา งอฉากขาเท้า" + (" (สมมติฐาน)" if asm else ""), asm=asm, pos=pts, zb=zb,
                         top=depth + above))
        sx_, sy_ = cb - 2 * cc, ch - 2 * cc
        hook = max(6 * dt, 75)
        cuts = ceil10(2 * (sx_ - dt) + 2 * (sy_ - dt) + 2 * hook)
        s = tie["s"]
        levels = [t - c]
        z = t + 50
        while z <= depth + 50:
            levels.append(z); z += s
        bars.append(dict(m="S1", t=tie["type"], d=dt, n=len(levels), shape="S", dims={"A": sx_, "B": sy_, "H": hook},
                         cut=cuts, c="--st", desc=f"ปลอกเสา @{s/1000:.2f}" + (" (สมมติฐาน)" if asm else ""), asm=asm,
                         levels=levels))
        if asm:
            warn.append(f"เหล็กเสา ({mn['n']}-{mn['type']}{dm}, ปลอก {tie['type']}{dt}@{s/1000:.2f}) ไม่ได้ระบุในแบบฐานราก — ใช้เป็นค่าสมมติฐาน ตรวจกับตารางเสาก่อนตัดจริง")

    for b in bars:
        b["dia"] = name(b["t"], b["d"])
        b["kgm"] = kgm(b["d"])
        b["g"] = grade.get(b["t"], "") + ("*" if assumed_grade else "")
        b["per"] = max(1, stock // b["cut"])
        if b["cut"] > stock:
            warn.append(f"{b['m']} ยาวตัด {b['cut']} มม. เกินความยาวเหล็กเส้น {stock} มม. — ต้องทาบต่อ")
    if assumed_grade:
        warn.append("ชั้นคุณภาพเหล็ก (" + "/".join(grade.values()) + ") ไม่ได้ระบุในแบบ — ใช้เป็นค่าสมมติฐาน")

    lean, sand = cfg.get("lean", 50), cfg.get("sand", 100)
    over = cfg.get("excavation_offset", 300)
    exc = (Bx + 2 * over) * (By + 2 * over) * (depth + lean + sand) / 1e9
    cb_, ch_ = (col["b"], col["h"]) if col else (0, 0)
    qty = [
        ("ขุดดิน (เผื่อข้างละ %.2f ม.)" % (over / 1000), f"{(Bx+2*over)/1000:.2f}×{(By+2*over)/1000:.2f}×{(depth+lean+sand)/1000:.2f}", exc, "ลบ.ม."),
        (f"ทรายหยาบบดอัด {sand/10:g} ซม.", f"{Bx/1000:.2f}×{By/1000:.2f}×{sand/1000:.2f}", Bx * By * sand / 1e9, "ลบ.ม."),
        (f"คอนกรีตหยาบ {lean/10:g} ซม.", f"{Bx/1000:.2f}×{By/1000:.2f}×{lean/1000:.2f}", Bx * By * lean / 1e9, "ลบ.ม."),
        ("คอนกรีตโครงสร้าง ฐานราก", f"{Bx/1000:.2f}×{By/1000:.2f}×{t/1000:.2f}", Bx * By * t / 1e9, "ลบ.ม."),
    ]
    if col:
        qty.append(("คอนกรีตโครงสร้าง ตอม่อ", f"{cb_/1000:.2f}×{ch_/1000:.2f}×{(depth-t)/1000:.2f}", cb_ * ch_ * (depth - t) / 1e9, "ลบ.ม."))
    fw = (2 * (Bx + By) * t + 2 * (cb_ + ch_) * (depth - t)) / 1e6
    qty.append(("แบบหล่อ ข้างฐาน + ตอม่อ", f"2×({Bx/1000:.2f}+{By/1000:.2f})×{t/1000:.2f} + 2×({cb_/1000:.2f}+{ch_/1000:.2f})×{(depth-t)/1000:.2f}", fw, "ตร.ม."))
    steel = sum(b["n"] * b["cut"] / 1000 * b["kgm"] for b in bars)
    qty.append(("ลวดผูกเหล็ก (≈1.5% น้ำหนักเหล็ก)", f"{steel:.2f}×0.015", steel * 0.015, "กก."))

    return dict(cfg=cfg, bars=bars, warn=warn, qty=[dict(item=a, f=b, v=round(v, 3), u=u) for a, b, v, u in qty],
                steel_kg=round(steel, 2), cover=c, stock=stock)


def build_html(calc, out):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    nm = calc["cfg"]["name"]
    html = tpl.replace("__TITLE__", f"{nm} Shop Drawing & Bar Cutting List") \
              .replace("/*__CALC__*/null", json.dumps(calc, ensure_ascii=False))
    p = os.path.join(out, "index.html")
    open(p, "w", encoding="utf-8").write(html)
    return p


def build_xlsx(calc, out):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    cfg = calc["cfg"]; nm = cfg["name"]; F = cfg["footing"]
    wb = Workbook(); ws = wb.active; ws.title = f"BBS {nm}"
    th = Side(style="thin"); B = Border(left=th, right=th, top=th, bottom=th)
    H = PatternFill("solid", fgColor="F4E3DA"); Y = PatternFill("solid", fgColor="FFF2B3")
    col = cfg.get("column")
    ws["A1"] = (f"BAR BENDING SCHEDULE / BAR CUTTING LIST — ฐานราก {nm} ({F['B']/1000:.2f}×{F['L']/1000:.2f}×{F['t']/1000:.2f} ม."
                + (f", ตอม่อ {col['b']/1000:.2f}×{col['h']/1000:.2f} ม.)" if col else ")"))
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = f"{cfg.get('project','')} · DWG {cfg.get('dwg','')} · REV {cfg.get('rev','0')} · {cfg.get('date','')} · ระยะ มม. / ความยาวตัด ม."
    ws["A3"] = f"จำนวนฐาน {nm}"; ws["C3"] = cfg.get("count", 1); ws["C3"].fill = Y; ws["C3"].font = Font(bold=True, size=13)
    ws["D3"] = "← กรอกจำนวนฐาน"
    hdr = ["Mark", "ขนาด", "ชั้นคุณภาพ", "รูปการดัด", "A (มม.)", "B (มม.)", "C/ทาบ/ขอ (มม.)", "ยาวตัด (ม./ท่อน)", "ท่อน/ฐาน",
           "รวม (ท่อน)", "ยาวรวม (ม.)", "กก./ม.", "น้ำหนัก (กก.)", f"ท่อน/เส้น {calc['stock']/1000:g} ม.", "ใช้เหล็กเส้น (เส้น)", "เศษ/เส้น (ม.)", "หมายเหตุ"]
    r0 = 5
    for i, h in enumerate(hdr, 1):
        c = ws.cell(r0, i, h); c.font = Font(bold=True); c.fill = H; c.border = B
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    shp = {"U": "U งอปลายขึ้น 90° 2 ข้าง", "O": "วงรัดรอบ สี่เหลี่ยม", "L": "L งอฉากขาเท้า", "S": "ปลอกสี่เหลี่ยม ขอ 135°"}
    S = calc["stock"] / 1000
    for k, b in enumerate(calc["bars"]):
        r = r0 + 1 + k; d = list(b["dims"].values()) + [None, None]
        note = b["desc"] + (" — ตรวจตารางเสา" if b.get("asm") else "")
        vals = [b["m"], b["dia"], b["g"], shp[b["shape"]], d[0], d[1], d[2], b["cut"] / 1000, b["n"], f"=I{r}*$C$3", f"=J{r}*H{r}",
                b["kgm"], f"=ROUND(K{r}*L{r},2)", b["per"], f"=ROUNDUP(J{r}/N{r},0)", f"=ROUND({S}-N{r}*H{r},2)", note]
        for i, v in enumerate(vals, 1):
            c = ws.cell(r, i, v); c.border = B
            c.alignment = Alignment(horizontal="left" if i in (4, 17) else "center", vertical="center", wrap_text=True)
        for i in (8, 11, 13):
            ws.cell(r, i).number_format = "0.00"
    rt = r0 + 1 + len(calc["bars"])
    ws.cell(rt, 12, "รวม (กก.)").font = Font(bold=True)
    ws.cell(rt, 13, f"=SUM(M{r0+1}:M{rt-1})").font = Font(bold=True); ws.cell(rt, 13).number_format = "0.00"
    dias = sorted({b["dia"] for b in calc["bars"]})
    for i, d in enumerate(dias):
        r = rt + 2 + i
        ws.cell(r, 1, f"สั่ง {d} ยาว {S:g} ม.")
        ws.cell(r, 3, f'=SUMIF(B{r0+1}:B{rt-1},"{d}",O{r0+1}:O{rt-1})'); ws.cell(r, 4, "เส้น")
        ws.cell(r, 5, f'=SUMIF(B{r0+1}:B{rt-1},"{d}",M{r0+1}:M{rt-1})'); ws.cell(r, 5).number_format = "0.00"; ws.cell(r, 6, "กก.")
    n = rt + 3 + len(dias)
    notes = ["หมายเหตุ:",
             f"1. ระยะหุ้มคอนกรีตฐานราก {calc['cover']} มม." + (f" · ระยะหุ้มเสา {col.get('cover',25)} มม." if col else ""),
             "2. ความยาวตัด = ผลรวมระยะภายนอก − หักการดัด 2d ต่อมุม 90° ปัดขึ้นทุก 10 มม."] + \
            [f"{i+3}. {w}" for i, w in enumerate(calc["warn"])]
    for tline in notes:
        ws.cell(n, 1, tline); n += 1
    for colL, wd in zip("ABCDEFGHIJKLMNOPQ", [7, 7, 10, 24, 9, 9, 11, 11, 9, 10, 11, 8, 11, 11, 13, 11, 42]):
        ws.column_dimensions[colL].width = wd
    ws.row_dimensions[r0].height = 34
    ws.page_setup.orientation = "landscape"; ws.page_setup.paperSize = ws.PAPERSIZE_A4; ws.page_setup.fitToWidth = 1
    q = wb.create_sheet("ปริมาณงานอื่น")
    q.append(["รายการ", "สูตร", "ต่อฐาน", "หน่วย", "รวมทุกฐาน"])
    for i, it in enumerate(calc["qty"], 2):
        q.append([it["item"], it["f"], round(it["v"], 3), it["u"], f"=C{i}*'BBS {nm}'!$C$3"])
    q.column_dimensions["A"].width = 32; q.column_dimensions["B"].width = 40
    for c in q[1]:
        c.font = Font(bold=True); c.fill = H
    p = os.path.join(out, f"{nm}-bar-cutting-list.xlsx")
    wb.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config"); ap.add_argument("--out", default=".")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    calc = compute(cfg)
    json.dump(calc, open(os.path.join(a.out, f"{cfg['name']}-calc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    h = build_html(calc, a.out); x = build_xlsx(calc, a.out)
    print("HTML :", h); print("XLSX :", x)
    for b in calc["bars"]:
        print(f"  {b['m']:3} {b['n']:>3}-{b['dia']:5} {b['shape']} dims={b['dims']} cut={b['cut']/1000:.2f} m  per{calc['stock']/1000:g}m={b['per']}")
    print(f"  steel/footing = {calc['steel_kg']} kg")
    for w in calc["warn"]:
        print("  WARN:", w)


if __name__ == "__main__":
    main()
