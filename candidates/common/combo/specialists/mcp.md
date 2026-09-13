# MCP servers

Use this note when implementing or debugging an MCP server, adding tools,
resources, or prompts, or changing its transport. MCP SDK APIs evolve, so check
the project's pinned package version and current official MCP documentation
before copying an exact registration signature.

## Keep the protocol surface explicit

- Tools perform actions, resources expose read-oriented data, and prompts are
  reusable parameterized templates. Give every exposed capability a stable
  name, useful description, input schema, and documented result shape.
- Define schemas before handlers. In a TypeScript server, use the SDK's current
  schema adapter or Zod and reject unknown or malformed input at the boundary.
  Validate authorization and filesystem/network targets in the handler too.
- Return structured, model-readable errors. Keep stack traces and secrets out
  of protocol responses, while logging a safe correlation id for diagnosis.

## Transport and lifecycle

- Keep tool/resource business logic independent of transport. The entrypoint
  should connect that logic to the selected SDK transport.
- Use stdio for a local client process and keep stdout reserved for protocol
  traffic. Send diagnostics to stderr. For remote clients, prefer the current
  Streamable HTTP transport; use legacy HTTP/SSE only for a compatibility need.
- Define startup, shutdown, and cancellation behavior. Close clients and stop
  background work when the transport disconnects.

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "example", version: "1.0.0" });
// Registration names/signatures vary by SDK release. Check the pinned docs.
const input = z.object({ query: z.string().min(1).max(200) });
```

## Safe operations

- Prefer idempotent tools, or make retry and duplicate effects explicit in the
  tool description and implementation. Bound external API calls, timeouts,
  pagination, and cost. Do not expose a general shell or arbitrary URL fetcher
  where a narrow capability is sufficient.
- Pin the SDK version, review release notes before upgrades, and run a client
  handshake plus one success and one validation-error call after transport or
  registration changes.
- Keep capability descriptions short and precise. They are part of the model's
  decision surface, so name side effects and required arguments clearly.

Source: ECC `mcp-server-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
