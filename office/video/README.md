# ชุดทำคลิปวิดีโอออฟฟิศ COST NINE (16 คลิป)

ใช้กับเว็บทำวิดีโอ AI แบบภาพเป็นวิดีโอ (Image to Video) ที่มีเครดิตฟรี เช่น Kling AI, Hailuo AI, Google Gemini (Veo) — ตรวจเงื่อนไขเครดิตฟรีและสิทธิ์การใช้งานเชิงพาณิชย์ของแต่ละเว็บก่อน

## วิธีทำ (ต่อ 1 คลิป)
1. เลือกโหมด Image to Video แล้วอัปโหลดภาพจากโฟลเดอร์ `images/` ตามตาราง
2. คัดลอก Prompt (ภาษาอังกฤษ) ของคลิปนั้นไปวาง
3. ตั้งค่า: ความยาว 5 วินาที, สัดส่วน 16:9, ปิดเสียง (ถ้ามีตัวเลือก)
4. ดาวน์โหลดเป็น MP4 แล้วตั้งชื่อไฟล์ตามคอลัมน์ "ชื่อไฟล์" เช่น `deliver.mp4`
5. ส่งไฟล์ให้ผม (แนบในแชต หรือใส่ไว้ใน repo ที่ `office/video/`) ผมจะใส่เข้าออฟฟิศสด ฉากไหนยังไม่มีคลิปจะเล่นภาพต่อเนื่องแทนเหมือนเดิม

เริ่มจาก 4 คลิปที่เห็นบ่อยสุดก่อน: `deliver`, `working`, `meet`, `report`

| # | ชื่อไฟล์ | ภาพต้นฉบับ (ใน `office/img/`) | ฉาก |
|---|---|---|---|
| 1 | `order.mp4` | `images/01-order.jpg` | เลขารับคำสั่งจากพี่โสภณ |
| 2 | `assign.mp4` | `images/02-assign.jpg` | หัวหน้ายื่นใบสั่งงานให้เลขา |
| 3 | `working.mp4` | `images/03-working.jpg` | วิศวกรถอดแบบที่โต๊ะ |
| 4 | `deliver.mp4` | `images/04-deliver.jpg` | วิศวกรส่งแฟ้ม BOQ ให้หัวหน้า |
| 5 | `revise.mp4` | `images/05-revise.jpg` | หัวหน้าชี้จุดที่ต้องแก้ |
| 6 | `issue.mp4` | `images/06-issue.jpg` | วิศวกรแจ้งปัญหาท่อชนคานกับเลขา |
| 7 | `meet.mp4` | `images/07-meet.jpg` | ทีมประชุมแก้ปัญหา |
| 8 | `agree.mp4` | `images/08-agree.jpg` | ได้มติ จับมือกัน |
| 9 | `handover.mp4` | `images/09-handover.jpg` | หัวหน้าส่งสรุปให้เลขา |
| 10 | `report.mp4` | `images/10-report.jpg` | เลขารายงานพี่โสภณ |
| 11 | `approve.mp4` | `images/11-approve.jpg` | พี่โสภณพิจารณาอนุมัติโพสต์ |
| 12 | `content.mp4` | `images/12-content.jpg` | ทีม Content ทำกราฟฟิก |
| 13 | `dev.mp4` | `images/13-dev.jpg` | ทีมเขียนโปรแกรมทำงาน |
| 14 | `train.mp4` | `images/14-train.jpg` | ห้องอบรม |
| 15 | `lobby.mp4` | `images/15-lobby.jpg` | ล็อบบี้ COST NINE |
| 16 | `tower.mp4` | `images/16-tower.jpg` | ตึก COST NINE สุขุมวิท |

## Prompt แต่ละคลิป

### 1. order.mp4 · เลขารับคำสั่งจากพี่โสภณ
```
The executive gestures at the drawing and explains; the secretary nods and writes on her tablet with a stylus, then looks up and smiles. Subtle natural head and hand movements. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 2. assign.mp4 · หัวหน้ายื่นใบสั่งงานให้เลขา
```
The team lead hands the printed work order sheet to the secretary; she takes it, glances at it and nods. Colleagues in the background keep typing. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 3. working.mp4 · วิศวกรถอดแบบที่โต๊ะ
```
The engineer slides the scale ruler along the drawing, glances at the monitor, types a number into the spreadsheet. The colleague behind her scrolls a floor plan. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 4. deliver.mp4 · วิศวกรส่งแฟ้ม BOQ ให้หัวหน้า
```
The engineer hands the bound BOQ folder to the seated team lead; the lead takes it with both hands, opens the cover, nods and smiles. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 5. revise.mp4 · หัวหน้าชี้จุดที่ต้องแก้
```
The team lead points at the highlighted area on the monitor and explains; the engineer nods and writes notes, then starts typing. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 6. issue.mp4 · วิศวกรแจ้งปัญหาท่อชนคานกับเลขา
```
The engineer tilts the tablet toward the secretary and points at the clash; she leans in, looks concerned, then writes in her notebook and nods. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 7. meet.mp4 · ทีมประชุมแก้ปัญหา
```
The three engineers discuss over the drawings; one points at the wall screen, another sketches on paper, the third nods. Natural conversation gestures. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 8. agree.mp4 · ได้มติ จับมือกัน
```
The two engineers finish a handshake and everyone smiles; the secretary types on her laptop; a relaxed atmosphere. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 9. handover.mp4 · หัวหน้าส่งสรุปให้เลขา
```
The team lead hands the bound report to the seated secretary; she takes it, opens it briefly and smiles. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 10. report.mp4 · เลขารายงานพี่โสภณ
```
The secretary presents the chart on her tablet and swipes to the next page; the executive reads the report, looks up and nods approvingly. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 11. approve.mp4 · พี่โสภณพิจารณาอนุมัติโพสต์
```
The executive scrolls the post on the tablet, pauses, then taps the screen to approve; the secretary smiles. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 12. content.mp4 · ทีม Content ทำกราฟฟิก
```
The content creator moves the mouse and adjusts the design on the monitor, then sits back slightly to review it; ring light glows softly. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 13. dev.mp4 · ทีมเขียนโปรแกรมทำงาน
```
The developers type on keyboards; code scrolls on the monitors; one turns the 3D house model on screen. City lights flicker outside. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 14. train.mp4 · ห้องอบรม
```
The instructor gestures at the slide while explaining; learners type on laptops and nod. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 15. lobby.mp4 · ล็อบบี้ COST NINE
```
Slow cinematic dolly-in toward the COST NINE logo wall; the light rings of the sculpture rotate slowly; soft reflections on the floor. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

### 16. tower.mp4 · ตึก COST NINE สุขุมวิท
```
The BTS skytrain glides past in the foreground; car light trails flow along the road; windows twinkle; slow upward tilt toward the tower. Keep the same people, faces, clothes, room and lighting as the image. Realistic human motion, static or very slow camera, no cuts, no new text, no subtitles.
```

## ใส่คลิปเข้าออฟฟิศสด
วางไฟล์ไว้ที่ `office/video/<ชื่อไฟล์>.mp4` แล้วเพิ่มบรรทัดในตัวแปร `VIDEOS` ของ `office/index.html` เช่น `deliver: "video/deliver.mp4"` (เลขาหรือ Claude ทำให้ได้) ฉากที่มีคลิปจะเล่นคลิปแทนภาพต่อเนื่อง
