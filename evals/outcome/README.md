# Paired outcome probes

## Shortcut-First evaluation

การทดลองนี้เปรียบเทียบ source snapshot ก่อนแก้กับ source ที่เพิ่มกฎ
Minimum sufficient work ใน shared context โดยใช้ fixture และ harness เดียวกัน
ไม่เพิ่ม skill ใหม่ ไม่ติดตั้ง service และไม่เปลี่ยน global model หรือ hooks

```powershell
python evals/outcome/run.py --baseline <pre-edit-source-snapshot> --output <results> --work-root D:/combo-shortcut-ab-run --repeat 3
```

ค่าเริ่มต้นคือ 8 กรณี x 3 คู่ รวม 48 model turns รันทีละ turn ด้วย
`gpt-5.6-luna` / `max`; ลำดับ baseline/patched สลับในแต่ละคู่ `--case` เลือก
กรณี และ `--repeat` ปรับได้ 1 ถึง 5 `--stage-only` เตรียม fixture โดยไม่เรียก
model; raw prompts, commands, events, usage, latency, changed-file hashes,
acceptance และ final answers เก็บแยกต่อแขน; generated execution workspace
ถูกลบหลังเก็บผล และ UI screenshots เก็บไว้ใน `visuals/`

หากรันขาดช่วง ใช้ output directory และ baseline เดิมพร้อม `--resume`; runner
จะอ่านเฉพาะ result files ที่บันทึกครบและรันแขนที่ยังไม่มีผลต่อ โดยเก็บ
continuation traces ไว้ใต้ run root เดิม

ถ้าเกิด environmental interruption กลางคู่ ให้ใช้ `--resume
--retry-environmental-pairs`; runner จะเก็บ raw files ของทั้งคู่ไว้ใต้
`attempts/pre-retry-N/` แล้วรันสองแขนใหม่เพื่อให้การเปรียบเทียบยังจับคู่กัน

| กรณี | หลักฐานที่วัด |
| --- | --- |
| Trivial label | แก้ label จุดเดียว, เป็น negative control สำหรับงานที่ไม่ควรขยาย workflow |
| Zero-value bug | แก้ regression และคงความหมายของ `None`, ใช้ independent tests |
| Inventory feature | เพิ่ม behavior บน iterable โดยคง defaults และ result shape, ใช้ independent tests |
| Security review | อ่านอย่างเดียว, ตรวจ ownership และ quantity zero |
| Research source triage | ตัดสินจากเอกสารสองรุ่น, ระบุวันที่และอธิบายความขัดแย้ง |
| Content repurpose | รักษาข้อเท็จจริงและเสียงแบรนด์, ไม่เผยแพร่ |
| UI reference | เปรียบเทียบ desktop/mobile ใน browser จริง, คง Save note และ persistence |
| Ambiguous export | อ่าน caller/contract, ไม่เขียน, ขอคำตอบเฉพาะ product choice ที่ยังไม่ชัด |

Mechanical pass ไม่เท่ากับคุณภาพโดยรวม: seeded tests ตรวจ defect ก่อนและหลัง,
read-only cases ตรวจ write commands/ไฟล์, และ UI acceptance ตรวจ geometry กับ
Save/reload จริง ส่วน trace, คำตอบเชิงเนื้อหา และ screenshots ต้องตรวจเพื่อดู
การตัดสินใจ, semantic fidelity, visual comparison, unnecessary work และ rework
Tokens ใช้ reported usage แยก cached input, output, tool calls และ latency
อย่าใช้ความยาวคำตอบแทน token usage

แต่ละแขนใช้ execution root แยกกัน และ process override ปิด installed Combo,
hooks, memory, MCP และ multi-agent เฉพาะรอบทดลอง ตัว runner ใช้
`danger-full-access`; hashes และ write-command checks ไม่ใช่ filesystem
isolation จึงจำกัดอยู่ที่ trusted synthetic fixtures Global host instructions
ยังเป็น confound ร่วมกัน ผล 8 cases x 3 pairs เป็น bounded sample เดียว ไม่ใช่
หลักฐานครอบคลุมทุก model, domain หรือ multi-turn rework

## Prior Outcome Ownership probes (historical)

การรันครั้งแรกใช้ workspace ใต้ run root เดียวกับ staged variants พบ baseline
coding อ่าน sibling fixtures และ patched UI สร้างภาพใน home สองไฟล์ จึงเป็น
host smoke evidence ที่มี scope errors ไม่ใช่ isolated A/B Source ของ harness
ต่อมาแยก execution roots และย้ำขอบเขตใน fixture instructions; ผลดิบเดิมคงไว้
ตามสภาพที่รันจริง แต่ไม่ใช้แทนการทดลอง Shortcut-First รอบนี้

หลังพบว่า patched รอบแรกยังเดา product choice จึงเสริม shared context ให้แยก
current behavior จาก requested intent แล้วรัน coding pair ใหม่ด้วย execution
roots ที่แยกแล้ว การตรวจ hashes ใน workspace ไม่ครอบคลุม side effects ภายนอก
จึงต้องอ่าน trace ร่วมด้วย ผลคู่นี้เป็นหลักฐานของ Outcome Ownership เท่านั้น
ไม่ใช่ผลประเมิน Minimum sufficient work

## Design source และ enforcement

อ่านต้นทาง [Matt Pocock grill-me](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grill-me/SKILL.md)
และ [grilling](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grilling/SKILL.md)
ที่ตรึงไว้ใน source library เดิม และตรวจ upstream ปัจจุบันก่อนปรับ
ใช้หลัก fact discovery, decision dependencies และ recommendations แต่ลดจาก
full interview เป็นคำถามเฉพาะผลลัพธ์/รสนิยม/ข้อจำกัดที่ยังตัดสินไม่ได้จริง
ไม่มีการนำ delegation mandate หรือ approval ceremony ของ upstream มาบังคับทุกงาน

เลือกใช้ independent acceptance และ completion gate ของ eval ซึ่งตรวจได้จริง
ไม่เพิ่ม global Stop hook: install manifests เดิมกัน hooks ไว้นอก ownership
และการเช็กเอกสารว่าระบุ "verified" ไม่พิสูจน์ความเหมือนหรือความจริงเชิง semantic
[Official hook documentation](https://learn.chatgpt.com/docs/hooks) อธิบาย host hooks
แต่ความสามารถของ host ไม่ได้ทำให้ universal taste gate เป็นไปได้
งานจริงยังใช้กฎใน shared context และ gate เดิมของ project, ไม่มี runtime hard
enforcement ที่รับประกันว่า agent ทุกตัวจะทำตาม skill
