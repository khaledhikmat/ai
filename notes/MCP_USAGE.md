# MCP Server Usage Guide

This guide explains how to use the new MCP server delegation architecture.

## Quick Start

### Running the Security MCP Server

```bash
# From project root directory
python3 mcp_server.py security

# Or using environment variable
export MCP_TYPE=security
python3 mcp_server.py
```

### Available MCP Servers

- **security**: Security knowledge base server for incident management

## Architecture Benefits

### Before (Direct Implementation)
```bash
# Had to run from specific directory with path issues
cd mcp/incidents
python mcp_server.py  # Hardcoded dependencies, path problems
```

### After (Delegation Pattern)
```bash
# Run from project root with clean dependency injection
python mcp_server.py security  # Services injected, no path issues
```

## How It Works

### 1. Service Injection
The MCP server uses the same services as agents:
- `EnvVarsConfigService` for configuration
- `Neo4jSecurityKnowledgeBaseService` for data operations
- Clean dependency injection pattern

### 2. Centralized Runner
The root `mcp_server.py` handles:
- Server type selection (environment var or CLI arg)
- Service initialization and cleanup
- Error handling and logging
- Consistent startup/shutdown process

### 3. Easy Extension
To add a new MCP server:

1. Create `mcp/newserver/server.py`:
```python
async def initialize_mcp_params() -> MCPServerParameters:
    # Initialize services and dependencies
    # Create FastMCP server
    # Register resources and tools
    return MCPServerParameters(...)

async def finalize_mcp_params(params: MCPServerParameters) -> None:
    # Clean up resources
```

2. Register in `mcp_server.py`:
```python
mcp_init_fns: MCP_INIT_FNS = {
    "security": init_security_mcp,
    "newserver": init_newserver_mcp,  # Add here
}
```

3. Run it:
```bash
python mcp_server.py newserver
```

## Environment Configuration

The MCP servers use the same environment variables as other components:

```bash
# Neo4j configuration (for security server)
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="admin4neo4j"

# MCP server selection
export MCP_TYPE="security"
```

## Integration with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "security-kb": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_server.py", "security"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## Resources Available

The security MCP server provides these resources:
- `security://employees` - All employees
- `security://officers` - Security officers  
- `security://visitors` - Visitors
- `security://vehicles` - Vehicles
- `security://campuses` - Campus locations
- `security://incidents` - Security incidents

## Tools Available

- `create_employee` - Create new employee records
- `create_officer` - Create security officer records
- `create_visitor` - Create visitor records
- `create_vehicle` - Create vehicle records
- `create_campus` - Create campus records
- `create_incident` - Create incident records
- `search_nodes` - Search any node type with filters
- `create_relationship` - Create relationships between nodes
- `get_relationships` - Get all relationships for a node

This architecture provides consistent, maintainable, and extensible MCP server management following the same patterns as the rest of the project.