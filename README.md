# Combo สำหรับ Codex และ Claude Code

Workflow pack ที่ออกแบบการทำงานร่วมกันใหม่จาก **Karpathy, Ponytail, Matt Pocock
และ ECC** ครอบคลุมทั้ง engineering และงานนอก coding

เลือกโครงสร้าง **12 ทางเข้าตามงาน + `combo` router + `combo-maintain` + `combo-author`**
ทุกทางเข้าใช้ workflow และ library ร่วมกัน อ่านเฉพาะส่วนที่ต้องใช้
`combo-author` เป็น explicit-only สำหรับปรับ pack หรือสร้างระบบแบบ Combo
จึงไม่ถูกเลือกอัตโนมัติจากคำขอทำงานปกติ
รายละเอียดการเลือกและผลทดสอบอยู่ใน [รายงาน A/B](audit/ab/DECISION.md)

**Outcome ownership และ decision triage:** แกนร่วมใน
[context](skills/combo/practices/context.md) ให้ agent ค้นงานที่จำเป็นจาก intent
หาข้อเท็จจริงเองก่อนถาม และรักษา spec/ทางเลือกที่ผู้ใช้ยืนยันไว้ ส่วน
[outcome evidence](skills/combo/practices/outcome-evidence.md) ใช้เฉพาะงานที่ต้อง
ตรวจ fidelity หรือ success signal ที่ยังพิสูจน์ผลไม่ได้ ไม่เพิ่ม skill หรือ global hook
ดูวิธีรันและข้อจำกัดของ [paired outcome probes](evals/outcome/README.md)

**ปรับ context และ output (14 กันยายน 2026):** ทุก workflow ใช้
[กฎเลือกหลักฐานร่วม](skills/combo/practices/context.md) เพื่ออ่านตามคำถามที่มีผลต่อ
การตัดสินใจ รักษา contract และข้อขัดแย้ง ใช้ผลตรวจที่ยัง valid และรายงานเฉพาะ
ผลกับหลักฐานที่จำเป็น โดยคงความลึกและ coverage ที่ผู้ใช้ขอ
ดู [ผลตรวจรอบนี้](audit/context-20260914/REPORT.md) และ
[โจทย์ context probes](evals/context/README.md)

**ติดตั้งใน Codex และตรวจแล้ว (10 กันยายน 2026):** discovery ครบ 14 entries
ในรอบนั้น ไฟล์ตรงกับ source และซ้อม rollback ผ่าน โดย config ส่วนอื่นและ M2D คงเดิม

**รอบ authoring (25 ตุลาคม 2026):** discovery ครบ 15 entries รวม `combo-author`
แบบ explicit-only, installed bytes ตรงกับ source และ config ที่ไม่ใช่ของ Combo คงเดิม

**Claude Code ติดตั้งแล้วเช่นกัน:** ปรับเป็น native Skill/Plan Mode/subagent,
discovery ครบ 14 entries ในรอบนั้น และทดสอบการเรียกอัตโนมัติใน session จริงแล้ว
รอบ authoring เพิ่ม `/combo-author` แบบ explicit-only รวมเป็น 15 skills
และ verify installed bytes ผ่าน ดู [Claude setup](adapters/claude/README.md)
และ [ผลตรวจ](audit/claude/REPORT.md)

## ใช้งาน

สั่งงานตามปกติได้ทั้งไทยและอังกฤษ ไม่ต้องจำชื่อ source pack หรือเรียกหลาย skill
ต่อกัน เช่น “แก้บั๊กนี้ให้เสร็จ”, “วางแผนก่อน ยังไม่แก้โค้ด”,
“ทำ brief นี้เป็น LinkedIn กับ email” หรือ “สอนเรื่องนี้พร้อมแบบฝึกหัด”

| งาน | ทางเข้าที่ตรงกับงาน |
| --- | --- |
| พัฒนา feature และ refactor ให้เสร็จ | `combo-deliver` |
| วินิจฉัยหรือซ่อม bug และ build failure | `combo-debug` |
| ออกแบบ requirement, architecture และแผน implementation | `combo-plan` |
| ตรวจ code, requirement และความเสี่ยง | `combo-review` |
| รัน checks หรือทดสอบ user journey | `combo-verify` |
| เข้าใจ code และเปรียบเทียบทางเลือกทางเทคนิค | `combo-investigate` |
| Research หลักฐาน ตลาด และคำถามเชิงวิชาการ | `combo-research` |
| เขียนเนื้อหา วิเคราะห์ voice และดัดแปลงหลายช่องทาง | `combo-content` |
| สอน ออกแบบแบบฝึกหัด บทเรียน และ course | `combo-learning` |
| วิเคราะห์ธุรกิจ การเงิน inventory และ operations | `combo-business` |
| Visual direction, 3D, motion, video และ multimedia | `combo-media` |
| จัดงาน triage backlog, handoff และปรับวิธีทำงาน | `combo-productivity` |

เมื่อคำขอคาบเกี่ยวหรือยังเลือกทางไม่ได้ ใช้ [combo](skills/combo/SKILL.md)
เป็น router สำรอง ใน Codex เรียก `$combo` หรือ `$combo-content` โดยตรงก็ได้
ส่วน Claude Code ใช้ `/combo` หรือ `/combo-content`
งานแปลประโยคเดียวและการแก้เล็กที่เข้าใจชัดทำ inline ได้
คำขอที่ให้ทำงานจนเสร็จจะไม่หยุดแค่แผน ส่วน plan-only และ review-only
จะรักษาจุดที่ผู้ใช้ขอให้หยุด

Native skills ยังรับผิดชอบการใช้ browser, เอกสาร, ภาพ, spreadsheet และเครื่องมือ
เฉพาะทาง Combo ช่วยเลือกกระบวนการและความรู้ที่เกี่ยวข้อง

## ปรับแต่งหรือสร้างระบบแบบ Combo

ใช้ `$combo-author` (Claude Code: `/combo-author`) เมื่อต้องการเพิ่ม แก้ หรือถอด
workflow, practice, entry, template หรือ host adapter ของ pack นี้ หรือสร้างระบบ
แบบ Combo ที่เล็กกว่าขึ้นมาเอง ทางเข้านี้เป็น explicit-only จึงไม่ถูกเลือกอัตโนมัติ
จากคำขอทำงานปกติ และไม่ใช่ task workflow

เริ่มจาก [authoring practice](skills/combo/practices/authoring.md) ซึ่งเป็นขั้นตอน
ตัดสินใจที่ agent ใช้จริง และ [คู่มือ authoring](docs/authoring.md) สำหรับเหตุผลของ
pattern, บันไดการเปลี่ยนแปลงที่เล็กที่สุด, host boundary, การติดตั้งแบบ manifest
และวิธีแยก structural checks ออกจาก behavioral evidence

ใช้ [`combo-maintain`](skills/combo-maintain/SKILL.md) สำหรับติดตั้ง อัปเดต
ตรวจสอบ หรือ rollback ของที่ติดตั้งแล้ว

## Optional `.combo/` project ecosystem

Opt-in project knowledge for accepted specs, proposed delta changes, evidence-backed retro, tested shortcuts and a generated routing index. This does not add a new workflow or global hook, and does not silently replace a project's existing OpenSpec source. See [project ecosystem](skills/combo/practices/project-ecosystem.md) and [verification economy](skills/combo/practices/verification-economy.md).

Use the stdlib CLI from the target project's root:

```bash
python /path/to/installed/combo/tools/project_kb.py init
python /path/to/installed/combo/tools/project_kb.py index
python /path/to/installed/combo/tools/project_kb.py lookup --area ai-commander --kind retro --digest
python /path/to/installed/combo/tools/project_kb.py check
```

`init` is explicit; use accepted specs as contracts, not model-authored approvals.

## ข้างในมีอะไร

```mermaid
flowchart TD
    Request[คำขอของผู้ใช้] --> Entry[เลือกทางเข้าที่ตรงกับงาน]
    Request --> Router[combo เมื่อคำขอคาบเกี่ยว]
    Router --> Entry
    Entry --> Workflow[Shared workflow หนึ่งเส้นทางหลัก]
    Workflow --> Practice[Practice หรือ specialist เมื่อจำเป็น]
    Workflow --> Library[ค้น reference ตาม domain]
    Workflow --> Native[Native tools สำหรับลงมือและตรวจผล]
```

- [12 workflows](skills/combo/workflows/) เป็นกระบวนการที่ออกแบบให้ทำงานร่วมกัน
- [Shared practices](skills/combo/practices/) และ [27 engineering specialists](skills/combo/specialists/INDEX.md) ใช้เพิ่มความลึกเฉพาะเรื่อง
- [Source library](skills/combo/references/library/INDEX.md) เก็บครบ **331 direct source entries** จาก 4 repositories พร้อม support files, source pins และ license notices
- [Authoring templates](skills/combo/templates/) และ [คู่มือปรับแต่ง pack](docs/authoring.md) สำหรับการเพิ่มหรือแก้ระบบ
- [POLICY.md](POLICY.md) รวมหลัก Karpathy/Ponytail สำหรับ engineering และกติกาเลือก workflow
- [DESIGN.md](DESIGN.md) อธิบายการตัดสินใจของ architecture

331 entries หมายถึงความครอบคลุมของต้นฉบับ ไม่ใช่ 331 integrations ที่รันผ่านแล้ว
ส่วนที่ทับกันถูกจัดเจ้าของใหม่ ส่วน persona, ตัวเลขตัวอย่าง, tracker, hooks,
memory และ installer ของ upstream ต้องปรับให้เข้ากับงานและ host จริง
ไม่มีการเปิดระบบเหล่านี้เพียงเพราะอ่าน reference

ต้นฉบับดึงจาก GitHub และตรึง revision ไว้ใน [sources.lock.json](sources.lock.json)
[Source manifest](curation/full-library.json) ระบุที่มา การจัดกลุ่ม การปรับลิงก์
และ hash ของไฟล์ ไม่ต้องโหลด library ทั้งหมดเข้า context ทุกครั้ง

## Agent หลักและ Luna Max

Agent หลักรับผิดชอบเจตนา workflow, architecture, tradeoffs และการยอมรับผลงาน
เมื่องานเหมาะกับ delegation และได้รับอนุญาต ใช้ `combo_worker` สำหรับงานอิสระ
ที่กำหนดขอบเขตชัด โดย [Codex adapter](adapters/codex/combo-worker.toml)
ตั้งเป็น **Luna Max** ไม่เปลี่ยน model หลักของผู้ใช้

Workflow ไม่มีชื่อ model ฝังอยู่ จึงใช้ร่วมกับ model อื่นได้
ผลทดลองรอบนี้วัด Luna Max เท่านั้น ยังไม่ใช่หลักฐาน auto-trigger ของทุก model

Claude Code ใช้ [native `combo-worker`](adapters/claude/agents/combo-worker.md)
แบบ `model: inherit` ตาม model หลักของ Claude พร้อมส่ง context และขอบเขตงาน
ให้ subagent อย่างชัดเจน ดู [Claude setup](adapters/claude/README.md)

## ผลเปรียบเทียบ

ทดสอบ Codex จริง 10 คู่ รวม 20 sessions และตรวจซ้ำเฉพาะ 2 คู่ที่ติดเวลาหรือ
มีผลต่างที่ต้องแยกสาเหตุ โดยใช้เนื้อหาเดียวกันทั้งสองแบบ
ดู [คำตัดสินพร้อม semantic review](audit/ab/DECISION.md) และ [metrics](audit/ab/metrics.md)

เลือก pack เพราะแบ่งเจตนาของงานได้ชัดและดูแลเนื้อหาร่วมกันได้สะดวก
ไม่ได้เลือกเพราะประหยัดกว่า: 8 คู่ที่จบครบทั้งสองฝั่งในรอบแรกใช้ uncached input
รวม A 214,099 และ B 236,597 tokens ผลเรื่องเวลาและคุณภาพต่างกันตามเคส
การค้นพบ skill ผ่านไม่ได้แปลว่าทุกคำตอบของ model ถูกต้องโดยอัตโนมัติ

## ติดตั้งและดูแล

กฎเอกสารและคอมเมนต์ใช้ [ต้นฉบับร่วม](skills/combo/practices/project-knowledge-rule.md)
ตัวติดตั้งใส่กฎนี้ในส่วน Combo ของ global `AGENTS.md` (Codex) และ `CLAUDE.md`
(Claude Code) โดยอัตโนมัติ ส่วน [project knowledge](skills/combo/practices/project-knowledge.md)
เป็นรายละเอียดที่ workflow อ่านตามความจำเป็น ไม่เพิ่ม skill หรือคลัง memory ใหม่

Codex ใช้คำสั่งด้านล่าง ส่วน Claude Code ใช้
[ตัวติดตั้งและคำแนะนำเฉพาะ Claude](adapters/claude/README.md)
Claude เว็บ/Cowork และ ChatGPT ทั่วไปอยู่นอกขอบเขตการติดตั้งนี้
เปิด task ใหม่เพื่อรับ skill listing และ role ปัจจุบัน หากแอปยังแสดงรายการเก่า
ให้เปิด Codex ใหม่ ทางเข้าตามงานและ `combo-maintain` มี
`allow_implicit_invocation: true` ส่วน `combo-author` ตั้งเป็น `false`
เพื่อให้เรียกได้เฉพาะเมื่อผู้ใช้ระบุ และมี global routing policy ประกอบการเลือก

```powershell
python scripts/prepare.py
python scripts/setup.py plan
python scripts/setup.py apply
python scripts/setup.py verify
```

ตัวติดตั้งเก็บ baseline, ownership index และ receipt สำหรับ rollback
แก้เฉพาะ package กับส่วนของ Combo ใน config/AGENTS.md รักษา Preferences,
M2D, hooks, MCP, credentials และ native skills ส่วนอื่น
ใช้ `$combo-maintain` เมื่อจะอัปเดต ตรวจสถานะ หรือย้อนกลับ และใช้
`$combo-author` เมื่อจะปรับโครงสร้าง pack เอง

Baseline ก่อนขยายอยู่ที่ [archive/v2-engineering](archive/v2-engineering/)
และ receipt เดิมยังเก็บอยู่ การ rollback จะหยุดเมื่อพบไฟล์ถูกแก้ภายหลัง
เพื่อไม่ทับงานใหม่ของผู้ใช้

ย้อนกลับไปก่อนการติดตั้งรอบขยายนี้:

```powershell
python scripts/setup.py rollback --receipt backups/20260909-163949-897900/receipt.json
```

หลักฐาน: [การติดตั้งและ rollback](audit/ab/installation-verification.json),
[การรักษา config และ M2D](audit/ab/preservation.json)
