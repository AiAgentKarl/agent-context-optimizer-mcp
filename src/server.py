"""Context Optimizer MCP Server — Löst das Context-Window-Overload-Problem."""

from mcp.server.fastmcp import FastMCP

from src.tools.optimizer import register_optimizer_tools

mcp = FastMCP(
    "Context Optimizer MCP Server",
    instructions=(
        "Solves the #1 problem with MCP servers: context window overload. "
        "Provides smart tool pruning, relevance scoring, context budget tracking, "
        "and recommendations for which tools to load for a given task. "
        "Reduces context usage by 40-60% while maintaining capability."
    ),
)

register_optimizer_tools(mcp)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
