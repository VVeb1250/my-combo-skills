+++
id = "area.combo"
area = "combo"
status = "accepted"
summary = "Project knowledge navigation, behavioral specs, records and index compiler"
paths = ["skills/combo/tools/**", "skills/combo/practices/project-ecosystem.md"]
tags = ["routing", "indexing"]
verify = ["skills/combo/tools/project_kb.py", "tests/test_project_kb_navigation.py"]
[[links]]
relation = "constrained_by"
target = "combo-project-ecosystem"
+++
# Combo project ecosystem

Read the [accepted project knowledge contract](../specs/project-ecosystem.md) before changing the index or record lifecycle. The [authoring practice](../../skills/combo/practices/project-ecosystem.md) and [compiler contract](../../docs/combo-index-v1.md) describe use and migration.

Verify from the repository root:

```sh
python skills/combo/tools/project_kb.py check
python -m unittest discover -s tests -p 'test_project_kb_*.py' -v
```
