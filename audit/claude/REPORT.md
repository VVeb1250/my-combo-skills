# Claude Code renovation result

ติดตั้งแล้วใน `C:\Users\VVeb1250\.claude` สำหรับ Claude Code 2.1.258
ใช้ common workflows/library จาก 4 source packs ชุดที่ตรึง revision ไว้เดิม
พร้อม Claude-specific entrypoints, global routing policy และ native worker

## ผลที่สังเกตได้

- Native `system/init` พบ Combo **14 skills** และ `combo-worker` ครบ
- Skill listing ทั้งหมดลดจาก **363 เป็น 58 entries** โดยยังมี native skills
  และ utilities ที่ไม่ทับกัน ตัวเลขนี้เป็นจำนวนรายการ ไม่ใช่ token benchmark
- `ecc:*`, `ecc-hubs:*`, `mattpocock-skills:*` และ `multi-model-orchestrator`
  ไม่ปรากฏใน discovery หลังติดตั้ง ไฟล์ของเดิมยังอยู่สำหรับ rollback
- Main model/effort คง `sonnet` / `high`; session ทดสอบรายงาน `claude-sonnet-5`

| คำขอธรรมชาติ | สิ่งที่เกิดขึ้นจริง | ผล |
| --- | --- | --- |
| วินิจฉัย `mean([])` โดยยังไม่แก้ | เรียก `combo-debug` และอ่าน debug workflow | อธิบาย division by zero จาก source/test และไม่แก้ไฟล์ |
| เพิ่ม summary และแก้ empty mean ให้เสร็จ | เรียก `combo-deliver` และอ่าน deliver workflow | แก้เฉพาะ `stats.py`, Claude รัน tests และ parent ตรวจซ้ำผ่าน 6/6 |
| สอน mutable default arguments | เรียก `combo-learning` และอ่าน learning workflow | ให้ตัวอย่างผิด, ตัวอย่างแก้, แบบฝึกหัด และไม่สร้างไฟล์ |
| แปลประโยคเดียว | ไม่เรียก Skill หรือโหลด workflow | ตอบคำแปลสั้นตรงคำขอ |

ใช้ 4 fresh sessions หลังติดตั้ง และ 1 baseline session ก่อนติดตั้ง
ไม่มีการใส่ชื่อ Combo ในคำขอทดสอบ ปิด hooks, auto memory, MCP และ session
persistence เฉพาะ process ทดสอบ เพื่อไม่ให้งาน fixture ไปปะปนกับ personal memory
ดู [ผลย่อและ tool evidence](smoke-summary.json) และ `smoke-*.json`

Semantic review: delivery ครบ contract รวมเลข 0, float, list ว่าง, เฉพาะ None
และไม่ mutate input; diagnosis รักษาจุดหยุด มี typo เล็กในประโยคท้าย
บทเรียนมี core explanation และตัวอย่างถูกต้อง แต่หมายเหตุเรื่อง tuple กว้างเกินไป
เพราะ tuple อาจมี mutable object อยู่ข้างใน ข้อจำกัดนี้เป็นคุณภาพคำตอบของเคส
ไม่ใช่ผลพิสูจน์ว่า workflow รับประกันความถูกต้องทุกคำตอบ

## การติดตั้งและการตรวจ

- Applied **599 paths**, installed bytes ตรง source
- Unit tests ทั้งโปรเจกต์ **45/45**, รวม Claude-specific tests 12 ข้อ
- Scoped Ruff และ Pyright ผ่าน
- Claude native validator ผ่านสำหรับ skills และ agents; skills root มี warning
  symlink เดิมของ `find-skills` ซึ่งไม่ใช่ Combo และไม่ได้แก้ในงานนี้
- ซ้อม rollback จาก actual receipt บนสำเนาครบ 599 paths ผ่าน
- ข้อความนอก Combo block ใน `CLAUDE.md` เหมือนเดิมทุก byte
- ตรวจ 827 file/config hashes เทียบ baseline ก่อน apply แล้วไม่เปลี่ยน
  ครอบคลุม Codex, Claude skills เดิม, RTK และ settings ส่วนที่ไม่เป็นเจ้าของ
  พบ `.codex/config.toml` เปลี่ยนจากภายนอกก่อนเริ่ม apply จึงเก็บทั้ง initial
  baseline และ pre-install baseline ไว้ โดยไม่ย้อนหรือทับการเปลี่ยนนั้น

หลักฐาน: [installation verification](installation-verification.json),
[preservation](preservation.json), [reviewed plan](plan-review.json)

Lexical audit ตรวจ installed Combo instruction files 575 ไฟล์ พบ 3 candidates
ที่ตรวจแล้วเป็น safety guidance 2 จุด และ URL ตัวอย่าง Mailtrap inbox ID 1 จุด
ไม่พบ hidden characters หรือคำสั่งส่ง secret ใน candidates เหล่านี้
ดู [audit](installed-audit.json); การสแกนรูปแบบไม่ใช่การรับรองความปลอดภัยทุกกรณี

## ขอบเขตหลักฐาน

ตรวจ auto-trigger บน Sonnet ในเคสข้างต้น ไม่ได้ทดสอบทุก model หรือทุก domain
Plan Mode และ worker ปรับตาม native host contract และตรวจ configuration/discovery
แต่รอบนี้ไม่ได้ทำ interactive plan approval หรือรัน delegated worker จริง
hooks และ MCP ของผู้ใช้คง settings เดิม แต่ไม่ได้ execute ใน smoke tests

เริ่ม Claude Code session ใหม่เพื่อใช้งานชุดนี้ พอแล้วสำหรับตอนนี้

Rollback transaction นี้:

```powershell
py scripts/setup-claude.py rollback --receipt backups/claude-20260910-031317-323800/receipt.json
```
