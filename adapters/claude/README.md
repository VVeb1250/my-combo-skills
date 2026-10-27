# Combo สำหรับ Claude Code

ใช้ 12 workflows, practices และคลังความรู้จาก Karpathy, Ponytail, Matt Pocock
และ ECC ร่วมกับ Codex แต่แยกวิธีติดตั้งและคำสั่งที่ขึ้นกับ host
ขอบเขตนี้คือ Claude Code บนเครื่อง ไม่ใช่ Claude เว็บหรือ Cowork

**ติดตั้งและตรวจแล้ว:** discovery ครบ 14 skills ในรอบนั้น, auto-trigger ผ่านใน
3 งาน และไม่โหลด workflow ในคำขอแปลสั้น ตรวจโค้ดที่ Claude สร้างผ่าน 6 tests
รอบ authoring เพิ่ม `/combo-author` แบบ explicit-only รวมเป็น 15 skills
และ verify installed bytes ผ่าน ดู [ผลทดสอบและขอบเขตหลักฐาน](../../audit/claude/REPORT.md)

## สิ่งที่ปรับให้ Claude

- 12 ทางเข้าตามงาน พร้อม `combo` router และ `combo-maintain` รวม 14 skills
  เปิดทั้ง automatic invocation และคำสั่ง `/combo-*`
- `/combo-author` เป็น explicit-only (`disable-model-invocation: true`,
  `user-invocable: true`) สำหรับปรับ pack หรือสร้างระบบแบบ Combo รวมเป็น 15 skills
- เลือก Skill tool หนึ่งทางหลัก แล้วอ่านเฉพาะ workflow และ references ที่จำเป็น
  แทนคำสั่งเดิมที่ให้อ่านทุก skill ที่อาจเกี่ยวข้อง
- ใช้ `${CLAUDE_SKILL_DIR}` อ้างไฟล์โดยไม่สมมติ working directory
- งานที่ขอให้สร้างจนเสร็จเดินต่อถึง implementation และ verification
  ส่วน plan-only, diagnosis-only และ Plan Mode รักษาจุดหยุดตามคำขอและ host
- `combo-worker` เป็น native Claude subagent แบบ `model: inherit`
  รับงานที่มีขอบเขตและ context ชัด ส่วน agent หลักตัดสินใจและตรวจการรวมงาน
  การเลือก Luna Max เป็นของ Codex adapter เท่านั้น
- ปิด discovery ของ plugins `ecc-hubs@bundle`, `ecc@ecc` และ
  `mattpocock-skills@mattpocock` พร้อมตั้ง `multi-model-orchestrator` เป็น `off`
  เพื่อหยุด router เก่าที่ซ้อนกัน โดยเก็บไฟล์เดิมไว้สำหรับ rollback

ไม่มีการเพิ่มสิทธิ์ผ่าน `allowed-tools`, บังคับ `context: fork`, เปลี่ยน model
หรือ effort หลัก หรือเปิด hooks และ memory ของ upstream ตามตัวอย่างใน library
settings hooks ของผู้ใช้และกฎ memory ของ Claude คงเดิม การปิด plugin เก่าจะปิด
ส่วนประกอบที่ plugin นั้นให้มาด้วย

## ใช้งาน

เริ่ม Claude Code session ใหม่แล้วสั่งงานตามปกติ เช่น
“หาสาเหตุที่ test นี้พัง ยังไม่แก้”, “ทำ feature นี้ให้เสร็จพร้อมตรวจผล” หรือ
“สอนเรื่องนี้พร้อมแบบฝึกหัด” หากต้องการเลือกตรง ใช้ `/combo-debug`,
`/combo-deliver`, `/combo-learning` หรือ `/combo` เมื่อคำขอคาบเกี่ยว

Auto-trigger อาศัย description และ global routing guidance จึงไม่ใช่การบังคับ
แบบ deterministic ผลตรวจจริงต้องแยกจากคำอธิบายโครงสร้าง

## ปรับแต่ง pack

ใช้ `/combo-author` เมื่อต้องการเพิ่ม แก้ หรือถอด workflow, practice, entry,
template หรือ host adapter ของ pack นี้ หรือสร้างระบบแบบ Combo ที่เล็กกว่าเดิม
ทางเข้านี้เป็น explicit-only จึงไม่ถูกเลือกอัตโนมัติจากคำขอทำงานปกติ
เริ่มจาก [authoring practice](../../skills/combo/practices/authoring.md) และ
[คู่มือ authoring](../../docs/authoring.md) ส่วนการติดตั้ง อัปเดต ตรวจสอบ หรือ
rollback ใช้ `/combo-maintain`

## ดูแลและ rollback

รันจาก source checkout นี้:

```powershell
py scripts/setup-claude.py plan
py scripts/setup-claude.py apply
py scripts/setup-claude.py verify
```

ตัวติดตั้งรวม common source กับ [Claude overrides](overrides/) ไม่แก้ package
ที่ติดตั้งใน Codex และไม่ติดตั้ง `agents/openai.yaml` ใน Claude
เก็บ baseline/receipt ไว้ใต้ `backups/` และรายงานใต้ `audit/claude/`
ใช้ receipt ของ transaction ที่ต้องการย้อน:

```powershell
py scripts/setup-claude.py rollback --receipt backups/claude-20260910-031317-323800/receipt.json
```

การ update และ rollback หยุดเมื่อพบการแก้ไขภายหลังในไฟล์ที่เป็นเจ้าของ
เพื่อให้ตรวจความต่างก่อนทับงานใหม่

รายละเอียดพฤติกรรมอ้างอิงอยู่ใน [official docs audit](../../audit/claude/official-docs.md)
และ [Claude execution guide](overrides/combo/references/claude-code.md)
