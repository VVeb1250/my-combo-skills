---
name: ecc-mcp
description: Build or debug an MCP server's tools, resources, prompts, schemas, or transport. Use when implementing MCP protocol integration. สร้างหรือแก้ MCP server. Skip ordinary tool use and generic API client work.
metadata:
  owner: ecc
---

# Implement the protocol boundary

Inspect the installed SDK and existing server. Verify version-sensitive APIs in
the SDK source or current official MCP documentation before copying examples.
Define narrow input schemas, clear output/error shapes, and tool semantics that
distinguish read-only operations from mutations without relying on annotations
as an authorization mechanism.

For stdio, reserve stdout for protocol messages and send diagnostics to stderr.
For HTTP transports, follow the actual authentication, session, cancellation,
and lifecycle requirements. Close resources and bound expensive operations.

Verify representative valid/invalid calls through the real transport. Do not
add a second transport, discovery service, or orchestration layer without need.
Read `references/upstream.md` for specific SDK examples, checking their version.
