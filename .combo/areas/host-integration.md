+++
id = "area.host-integration"
area = "host-integration"
status = "accepted"
summary = "Codex and Claude Code installation, owned policy blocks, adapter migration and rollback"
paths = ["scripts/setup.py", "scripts/setup-claude.py", "adapters/**", "install-manifest.json"]
verify = ["tests/test_setup.py"]
+++
# Host integration

Use the [maintenance practice](../../skills/combo/practices/maintenance.md) for host ownership, installation and rollback. Preserve unrelated user files and settings. Verify with `python -m unittest discover -s tests -p 'test_setup.py' -v` and the Claude installer tests.
