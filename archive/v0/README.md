# Combo สำหรับ Codex

ติดตั้งเฉพาะ Codex ตาม scope ล่าสุด ใช้หลักจาก GitHub ของ Karpathy, Ponytail,
Matt Pocock และ ECC โดย pin commit ใน [sources.lock.json](sources.lock.json)
ชุดนี้เป็นการ distill ที่ปรับให้ตรงกับวิธีทำงานของเจ้าของเครื่อง ไม่ใช่การติดตั้ง
upstream ทั้งแพ็กตรง ๆ

## ใช้งาน

ปิดเปิด Codex แล้วเริ่ม task ใหม่ เพื่อให้รายชื่อ skill และ global instructions
สะท้อนชุดใหม่ครบ โดยเฉพาะ plugin ที่ถูกปิดใน config

อธิบายงานตามปกติได้ทั้งไทยและอังกฤษ ไม่ต้องพิมพ์ชื่อ skill ทุกครั้ง
การเลือกอัตโนมัติเปิดอยู่ครบ 17 skill แต่ยังขึ้นกับการตัดสินใจของแต่ละ model
ถ้าต้องการบังคับเลือกเฉพาะงาน ใช้ `$matt-tdd`, `$matt-review`, `$ecc-build-fix`
หรือชื่อที่ตรงกับตารางด้านล่าง

| หน้าที่ | เจ้าของที่ใช้งาน |
|---|---|
| หลักคิดและขอบเขตการแก้ | Karpathy ใน global AGENTS.md |
| ลดความซับซ้อนโดยรักษา requirement | Ponytail ใน global AGENTS.md |
| วางแผน / TDD / review | matt-plan / matt-tdd / matt-review |
| ตรวจความซับซ้อน | ponytail-review |
| Security / build / E2E | ecc-security-review / ecc-build-fix / ecc-e2e |
| ตรวจเฉพาะภาษา / ฐานข้อมูล | ecc-language-review / ecc-database |
| API / React / Python / Rust / MCP | ecc-api-design / ecc-react / ecc-python / ecc-rust / ecc-mcp |
| ค้นหลักฐาน / ดูแล setup / คลังเฉพาะทาง | codex-research / codex-setup / codex-library |

POLICY.md มี 49 บรรทัด ติดตั้งใน `C:/Users/VVeb1250/.codex/AGENTS.md`
โดยเก็บ Preferences และ Memory section เดิมไว้ ส่วน skill ติดตั้งใน
`C:/Users/VVeb1250/.codex/skills`

ปิด ECC และ Caveman plugin เฉพาะใน Codex เพื่อไม่ให้ชุดใหญ่เปิด owner ซ้ำ
skill เดิมที่ชนถูกปิดผ่าน `[[skills.config]]` ตาม path ไม่มีการลบต้นฉบับ
คลัง specialist ที่เก็บไว้มี catalog สำหรับค้นเฉพาะเรื่อง โดยให้ต้นฉบับ GitHub
ที่เพิ่งดึงมามีลำดับก่อนสำเนาเก่าเมื่อชื่อซ้ำกัน
native plugins และ utility ที่มีหน้าที่ต่างกันยังคงอยู่

## หลักฐานและขอบเขตของผล

- [baseline](audit/baseline-codex.json) และ [หลังติดตั้ง](audit/after-codex.json):
  รายชื่อจริงจาก Codex app-server ไม่ใช่การนับโฟลเดอร์อย่างเดียว
- [ผลตรวจรูปแบบ](audit/curated-validation.json): frontmatter มาตรฐาน,
  description ไม่เกิน 400 ตัวอักษร, auto invocation, reference และขนาด policy
- [manifest](manifest.json): decision ครบ 998 แถว รวม corpus 981 ไฟล์และชุดใหม่ 17 ตัว
- [เหตุผลการปรับ](audit/DECISIONS.md) และ [semantic review](audit/semantic-review.md)
- `python -m unittest discover -s tests -v`: ตรวจ idempotence, การรักษา config,
  rollback คืน byte เดิม และการไม่เขียนทับ user edit ที่เกิดภายหลัง
- [smoke review](audit/smoke-review.txt): session ใหม่ของ Luna Max อ่าน matt-review
  และ ecc-security-review จริง แล้วพบ authorization bug กับ zero-value bug
- [negative smoke](audit/smoke-negative.txt): ทดสอบแปลข้อความซึ่งไม่ควรเรียกงาน code

จำนวนตัวอักษร description ไม่ใช่ token cost จริง และรายการ enabled รวม skill
ที่เจ้าของเดิมตั้ง explicit-only ไว้ด้วย ดูตัวเลขที่สรุปใน audit/summary.json
ยังไม่ได้วัด intervention rate ของ 15 งานจริงหรือ benchmark ครบทุก model
[eval prompts](evals/evals.json) เป็นชุดเคสที่เตรียมไว้ ไม่ใช่ผลผ่าน 15 งาน
ทดสอบ smoke แบบ ephemeral, read-only และปิด hooks เฉพาะ process ทดสอบ

## ตรวจซ้ำหรือ rollback

รันจาก `D:/0_person-project/my-combo-skills`:

```powershell
python scripts/setup.py verify
python scripts/codex_inventory.py --output audit/current-codex.json
```

คืนค่าก่อนเริ่มงานนี้ด้วยคำสั่งเดียว:

```powershell
python scripts/setup.py rollback --receipt backups/original-state/receipt.json
```

Rollback ตรวจ hash ทุกไฟล์ก่อนเริ่ม หากมีการแก้ไฟล์หลังติดตั้งจะหยุดให้จัดการ
ความต่างก่อน ไม่มี recursive delete และไม่ทิ้งการแก้ของคนอื่น
backup อยู่เฉพาะเครื่องและถูก exclude จาก git เพราะมีสำเนา config ส่วนตัว

หากแก้ชุด source ในภายหลัง ให้ตรวจ diff และทดสอบก่อน:

```powershell
python scripts/prepare.py
python scripts/setup.py plan
python scripts/setup.py apply
```

`apply` บังคับตรวจรูปแบบก่อนเขียน และเก็บ receipt ของการเปลี่ยนครั้งนั้นใหม่
`original-state` เป็น snapshot ของงานติดตั้งครั้งนี้ ไม่ใช่การตามเก็บทุก update
การ update GitHub ต้อง fetch/review แล้ว pin commit ใหม่โดยตั้งใจ ไม่มี updater
ที่เปลี่ยน behavior เงียบ ๆ

## สิ่งที่เลื่อนไว้

Claude และ ChatGPT เว็บ/แอปทั่วไปยังไม่ได้เปลี่ยนตามคำสั่ง scope ล่าสุด
ไม่มี runtime orchestrator, workflow compiler, IR, graph หรือ enforcement hooks ใหม่
การทดลอง budget 2-3 วันถูกข้ามตามที่เจ้าของอนุญาต และไม่อ้างว่าทดลองแล้ว

เอกสาร host ที่ตรวจอ้างอิง:
[Codex skills](https://developers.openai.com/codex/skills)
และโครงสร้าง API ที่ generate จาก CLI 0.147.0 บนเครื่องนี้
ต้นฉบับและ license ที่พบอยู่ใน sources/ และ licenses/ ตามลำดับ
