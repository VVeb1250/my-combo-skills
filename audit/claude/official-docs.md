# Claude Code official-docs audit

ตรวจเอกสารทางการของ Anthropic/Claude Code ณ 2026-09-10 เพื่อใช้ปรับ Combo pack
ข้อเท็จจริงด้านล่างเป็น documented behavior ไม่ใช่การอนุมานคุณภาพหรือพฤติกรรมของ model

## Skills และ personal discovery

- Personal skill อยู่ที่ `~/.claude/skills/<name>/SKILL.md` และใช้ได้กับทุก project บนเครื่องนั้น ส่วน project skill อยู่ที่ `.claude/skills/<name>/SKILL.md`; ยังมี managed, nested, `--add-dir` และ plugin scopes ตาม [Skills](https://code.claude.com/docs/en/skills#where-skills-can-live).
- โฟลเดอร์ของ skill กลายเป็นชื่อ command และ `SKILL.md` ต้องมี YAML frontmatter ตั้งแต่บรรทัดแรก `description` ช่วยให้ Claude จับคู่การใช้งานอัตโนมัติ.
- เมื่อเริ่ม session Claude เห็นชื่อและ description ก่อน ส่วน body โหลดเมื่อ skill ถูก invoke; ผู้ใช้เรียกด้วย `/name` และ Claude เรียกผ่าน `Skill` tool. ค่าเริ่มต้นเปิดทั้งสองทางตาม [Skills](https://code.claude.com/docs/en/skills#invoke-skills).
- สำหรับ repo นี้ router ปัจจุบันอยู่ที่ [`skills/combo/SKILL.md`](../../skills/combo/SKILL.md) และมี direct workflow entries หลายตัว. การติดตั้งแบบ personal กับแบบ project จึงเป็นคนละ deployment choice ที่ parent ต้องตัดสินจาก intended scope.

## Frontmatter ที่มีผลต่อ invocation

| Field | พฤติกรรมที่ documented | ผลต่อการย้าย Combo |
|---|---|---|
| `disable-model-invocation: true` | ผู้ใช้เรียกด้วย `/name` ได้ แต่ Claude เรียกไม่ได้ และ description ไม่อยู่ใน model context | ใช้กับขั้นตอนที่ต้อง explicit เท่านั้น |
| `user-invocable: false` | ซ่อนจากเมนู `/` แต่ยังอยู่ใน context และ Claude เรียกได้; field นี้ควบคุม menu visibility ไม่ใช่ Skill tool access | เหมาะกับ helper ที่ไม่ควรเป็น user command |
| `context: fork` | รันใน isolated subagent context; ไม่มี conversation history ของ parent. `agent` เลือก agent type, ค่าเริ่มต้นคือ `general-purpose`; `background: false` ใช้รอผลใน turn เดียวกันเมื่อ version รองรับ | ใช้เมื่อ workflow ต้องแยกบริบท ไม่ควรถือว่าเป็น Codex worker equivalent โดยอัตโนมัติ |
| `agent` | รับ `Explore`, `Plan`, `general-purpose` หรือ custom agent จาก `.claude/agents/` เมื่อใช้กับ fork | ต้องตรวจ custom agent ที่มีอยู่จริง |
| `allowed-tools` | ให้ permission prompt-free สำหรับ tools ที่ระบุใน turn ของ skill; ไม่ใช่ allowlist ที่ตัด tool อื่น และ permission settings ยังมีผล | review skill body ก่อนให้สิทธิ์กว้าง |
| `model`, `effort` | override model/effort ของ turn หรือ fork ตาม context | portable source ควร model-neutral |

รายละเอียด field เหล่านี้อยู่ใน [Skills frontmatter](https://code.claude.com/docs/en/skills#frontmatter-reference). `allowed-tools` ใน skill frontmatter ใช้กับ CLI; [Agent SDK skills](https://code.claude.com/docs/en/agent-sdk/skills#skill-configuration) ระบุว่า SDK จะ ignore field นี้ และให้ใช้ query option `allowedTools` แทน.

## ไฟล์อ้างอิงและ path

- เอกสาร Skills วาง supporting files ไว้ข้าง `SKILL.md` และแสดง relative markdown link เช่น `[reference.md](reference.md)`. สำหรับคำสั่งหรือ script ที่ต้องคงที่ข้าม working directory ให้ใช้ `${CLAUDE_SKILL_DIR}` (โฟลเดอร์ที่มี `SKILL.md`) และ `${CLAUDE_PROJECT_DIR}`; injected shell ยังเริ่มจาก shell working directory ปัจจุบัน ตาม [Skills dynamic context](https://code.claude.com/docs/en/skills#claude_code-specific-features).
- อย่าสรุปว่า current working directory คือ skill directory. ใน pack ควรตรวจ links และ shell paths หลังติดตั้งจริง.

## CLAUDE.md, rules และ plan mode

- Claude Code โหลด `CLAUDE.md` และ `CLAUDE.local.md` จาก managed, user, project และ ancestor scopes; `AGENTS.md` ไม่ใช่ชื่อไฟล์ที่ Claude โหลดเอง. หากต้องใช้กฎเดิม ให้มี `CLAUDE.md` ที่ import `@AGENTS.md` ตาม [Memory](https://code.claude.com/docs/en/memory#claude-md-imports).
- `@path` imports ซ้อนกันได้ลึกสุด 5 ระดับ และ relative import อิงไฟล์ที่มี import ไม่ใช่ working directory. `.claude/rules/*.md` ถูกค้นหาแบบ recursive; rule ที่ไม่มี `paths` โหลดทุก session ส่วน rule ที่มี `paths` ทำงานเมื่อไฟล์ที่ match ถูกอ่าน.
- CLAUDE.md เป็น guidance ใน context ไม่ใช่ enforcement boundary. ใช้ permissions หรือ hooks หากต้องบังคับ behavior; `/memory` ใช้ตรวจไฟล์ที่โหลด ตาม [How Claude remembers](https://code.claude.com/docs/en/memory).
- `plan` เป็น permission mode สำหรับอ่านไฟล์และ read-only shell exploration แล้วเสนอแผน. เข้าได้ด้วย `/plan`, `Shift+Tab` หรือ `claude --permission-mode plan`; เมื่อผู้ใช้อนุมัติแผนจึงเลือกโหมดแก้ไข. คำขอ plan-only ควรคงสถานะ planning และเลือก refine/keep planning โดยไม่อนุมัติ. `bypassPermissions` อาจข้าม enforcement นี้ได้ ดังนั้นอย่าใช้ plan mode เป็น security boundary ตาม [Permission modes](https://code.claude.com/docs/en/permission-modes#plan-mode).

## Personal subagents

- Personal agent file อยู่ที่ `~/.claude/agents/<name>.md` และใช้ได้ทุก project. YAML ต้องมี `name` และ `description`; markdown body คือ system prompt. Fields ที่เกี่ยวข้องได้แก่ `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation` และ `initialPrompt` ตาม [Subagents](https://code.claude.com/docs/en/sub-agents#configure-subagents).
- ถ้าไม่ระบุ `tools` agent จะ inherit tools ที่ subagent ใช้ได้. `disallowedTools` ถอน tools ออกจาก inherited หรือ explicit set. `skills` preload full skill body ตอน startup แต่ไม่ได้จำกัด skill ที่ค้นพบหรือเรียกได้; ถ้าต้องบล็อกการเรียก skill ให้เอา `Skill` ออกจาก tools หรือใส่ใน `disallowedTools`.
- `model` รองรับ alias `sonnet`, `opus`, `haiku`, `inherit` และ full model ID. `inherit` ใช้ model ของ parent; resolution ยังขึ้นกับ invocation, frontmatter และ environment ตามเอกสารเดียวกัน. อย่า pin model ใน portable Combo source.
- `permissionMode` ที่ใช้บ่อยคือ `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`; parent permission mode บางแบบมี precedence เหนือ agent. Agent ใหม่ไม่มี parent conversation history; CLAUDE.md hierarchy และ preloaded skills เป็น input แยกต่างหาก.

## Description budget

- Skill listing ถูกใส่ใน context ของแต่ละ turn. เอกสารปัจจุบันกำหนด budget โดยประมาณ 1% ของ model context window; เมื่อเกิน budget จะตัด description ของ skill ที่ถูกใช้น้อยก่อน. `description` รวม `when_to_use` ได้ไม่เกิน 1,536 characters ต่อ skill โดยค่าเริ่มต้น ตาม [Skill descriptions](https://code.claude.com/docs/en/skills#troubleshooting).
- วาง use case สำคัญไว้ต้น description และทำให้สั้น. `/doctor` ประเมิน listing cost; `/skill-doctor` ช่วยตรวจ skill ใน version ที่รองรับ. มี settings `skillListingBudgetFraction`, `skillListingMaxDescChars` และ `SLASH_COMMAND_TOOL_CHAR_BUDGET` สำหรับปรับ budget.

## ตรวจ discovery โดยไม่เปิดเผยข้อมูล

- `claude agents` ใน CLI ปัจจุบันเปิด agent view สำหรับ monitor/dispatch parallel background sessions ไม่ใช่ configured-subagent inventory. ใช้ `/agents` ใน interactive session หรือ SDK init `agents` field เมื่อต้องการ agent configuration; `claude plugin validate <plugin-root>` ใช้ตรวจ packaged plugin และ frontmatter ของ component ใน plugin ตาม [CLI reference](https://code.claude.com/docs/en/cli-usage), [Plugin reference](https://code.claude.com/docs/en/plugins-reference) และ [Debug configuration](https://code.claude.com/docs/en/debug-your-config).
- วิธีที่ให้รายการ skill จริงจาก SDK คืออ่าน `system/init` แล้วเก็บเฉพาะ `message.skills` และ `message.slash_commands`; ใช้ fixture directory, `settingSources: ["user", "project"]`, `skills: "all"`, `maxTurns: 1` และหยุดทันทีหลัง init. นี่เป็น `query` ที่มี prompt จึงไม่ใช่การรับประกันว่าไม่มี model request. SDK จะค้นหา `~/.claude/skills/`, project `.claude/skills/` และ parent directories ตาม [Agent SDK skills](https://code.claude.com/docs/en/agent-sdk/skills#how-skills-work).
- `claude -p --output-format json` ให้ผลลัพธ์และ session metadata ของ one-shot แต่ JSON ไม่ใช่ discovery manifest. `--output-format stream-json --verbose` แสดง `system/init` ก่อน assistant turn; เอกสารไม่ได้รับรอง CLI mode ที่ emit manifest แล้วจบก่อน model request. หากมี authorization ให้ probe ที่ harmless ด้วย `--no-session-persistence --tools ""`; ยังเป็น model run ที่อาจมีค่าใช้จ่าย จึงไม่ได้รันใน audit นี้ ตาม [Headless session metadata](https://code.claude.com/docs/en/headless#read-session-metadata).
- สำหรับ process-only startup smoke ให้สร้าง temporary settings file ที่มี `{"disableAllHooks":true,"autoMemoryEnabled":false}` แล้วใช้ `claude --init-only --settings <temporary-settings.json>`. `--init-only` รัน Setup และ SessionStart hooks แล้วออกโดยไม่เริ่ม conversation; `disableAllHooks:true` ปิด hooks ที่ไม่ใช่ managed policy และ `autoMemoryEnabled:false` ปิดการอ่าน/เขียน auto memory. `--settings` มีผลเฉพาะ session และยังอยู่ใต้ managed settings ตาม [Settings](https://code.claude.com/docs/en/settings#change-a-setting-for-one-session), [Hooks](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks) และ [Memory](https://code.claude.com/docs/en/memory#enable-or-disable-auto-memory). คำสั่งนี้ไม่รับรอง `system/init` หรือ skill manifest.
- SDK `startup()` มี documented initialize handshake ก่อน prompt และ `WarmQuery.close()` ปิด process โดยไม่ส่ง prompt แต่ handle นี้ไม่ expose `system/init` arrays. จึงใช้ตรวจ process startup ได้ แต่ไม่ควรอ้างว่าเป็น model-free skill discovery ตาม [TypeScript SDK reference](https://code.claude.com/docs/en/agent-sdk/typescript#startup).
- อย่าพิมพ์ prompt, account data, `cwd`, plugin paths หรือ session metadata ลง log. การตรวจนี้ยืนยันสิ่งที่ Claude ค้นพบจริง แต่ไม่ยืนยันว่า workflow ตรง requirement ทุกข้อ.

## Delta จาก Codex pack

- Codex pack ปัจจุบันแยก router/workflow source จาก host-specific model config ใน [`adapters/codex/combo-worker.toml`](../../adapters/codex/combo-worker.toml). Claude ไม่มี adapter TOML แบบเดียวกัน; model/permission/agent behavior อยู่ใน CLI settings, skill/agent frontmatter และ SDK query options.
- ดังนั้นควรคง workflow source ให้ model-neutral แล้วทำ Claude installation/discovery adapter แยก. Claude automatic invocation ขึ้นกับ description budget และ invocation flags, ขณะที่ `/name` เป็น explicit user route. นี่เป็น native surface difference ไม่ใช่ข้ออ้างเกี่ยวกับความสามารถของ model.
- ก่อนประกาศแพ็ก ให้ตรวจ exact discovered names, links และ frontmatter ด้วยคำสั่งข้างต้นบน fixture ที่ไม่มีข้อมูลลับ. พอแล้วสำหรับเอกสาร audit นี้; ยังต้อง validate installation จริงก่อนใช้.

## Limits and provenance

## Local verification by the parent

- Installed CLI reports `2.1.258`. Its `agents --help` is for background sessions.
- `claude plugin validate C:\Users\VVeb1250\.claude\skills` accepted the standalone
  personal skills directory and passed, with one preexisting symlink warning.
  This observed CLI support extends beyond the plugin-root example above.
- A real baseline `--print --output-format stream-json --verbose` probe completed
  with `disableAllHooks:true`, `autoMemoryEnabled:false`, strict empty MCP and
  `--no-session-persistence`. It yielded native skill and agent arrays, used no
  tools, and reported `claude-sonnet-5`. See `smoke-baseline.json`.

## Research limits

อ้างอิงเฉพาะเอกสารทางการ Anthropic/Claude Code ที่ลิงก์ไว้ข้าง claim. Version-sensitive details ได้แก่ CLI flags, SDK schema, `/agents` behavior และ `skillListingBudget`; ตรวจ version ที่ติดตั้งอีกครั้งก่อน automation. ไม่ได้รัน model session, ไม่ได้อ่าน credentials และไม่ได้แก้ global configuration.
