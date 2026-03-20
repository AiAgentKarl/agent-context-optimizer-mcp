# Agent Context Optimizer MCP ⚡

Solves the **#1 problem** with MCP servers: **context window overload**.

When you have 10+ MCP servers installed, their tool schemas can consume 40-50% of your context window — leaving less room for actual conversation. This server fixes that.

## What it does

- **Analyzes your task** and recommends only the servers you actually need
- **Estimates token usage** for any combination of servers
- **Optimizes your server set** by identifying which servers to unload
- **Suggests minimal configurations** for maximum context efficiency

## Installation

```bash
pip install agent-context-optimizer-mcp
```

## Usage with Claude Code

```json
{
  "mcpServers": {
    "optimizer": {
      "command": "uvx",
      "args": ["agent-context-optimizer-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `analyze_task` | Analyze a task and recommend optimal server combination |
| `estimate_context_usage` | Estimate context window consumption for servers |
| `get_server_catalog` | Full catalog of known MCP servers with categories |
| `optimize_server_set` | Optimize currently loaded servers for a task |
| `suggest_minimal_set` | Recommend the absolute minimum servers needed |

## Example

```
"I need to check the safety of a Solana token"
→ Recommends: solana (required)
→ Saves: 85% context tokens vs loading all servers
```

## Why this matters

- Average MCP server uses ~3,000 tokens for tool schemas
- 10 servers = ~30,000 tokens = 15% of a 200k context window
- 20 servers = ~60,000 tokens = 30% wasted on tool definitions
- This optimizer helps you load only what you need

## License

MIT
