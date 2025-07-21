from typing import Callable, Awaitable, Any
from dataclasses import dataclass, field


@dataclass
class MCPServerParameters:
    """Configuration for MCP servers."""
    name: str
    description: str
    deps: Any = field(default=None, repr=False)
    server: Any = field(default=None, repr=False)  # fastmcp.FastMCP when available


# Type aliases for MCP server initialization and finalization functions
MCP_INIT_FNS = dict[str, Callable[[], MCPServerParameters]]
MCP_FIN_FNS = dict[str, Callable[[MCPServerParameters], None]]