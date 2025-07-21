# MCP Server HTTP Setup Guide

## Testing HTTP Transport Locally

### Step 1: Start MCP Server with HTTP Transport

```bash
# Set environment variables for HTTP mode
export MCP_TRANSPORT=http
export PORT=8000
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=admin4neo4j

# Start the server
python mcp_server.py security
```

You should see output like:
```
INFO:mcp-runner:Starting Security Knowledge Base MCP server...
INFO:mcp-runner:Starting MCP server on HTTP 0.0.0.0:8000
```

### Step 2: Test HTTP Server

Open a new terminal and test the server:

```bash
# Test if server is running
curl http://localhost:8000

# Test health endpoint (if available)
curl http://localhost:8000/health
```

### Step 3: Configure Claude Desktop

#### Option A: Replace your existing config
Edit your Claude Desktop MCP settings file and replace the content with:

```json
{
  "mcpServers": {
    "security-kb-http": {
      "url": "http://localhost:8000",
      "transport": "http"
    }
  }
}
```

#### Option B: Add alongside existing config
Or add the HTTP server alongside your existing stdio config:

```json
{
  "mcpServers": {
    "security-kb-stdio": {
      "command": "python",
      "args": ["/Users/khaled/github/ai/mcp_server.py", "security"],
      "cwd": "/Users/khaled/github/ai",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "admin4neo4j"
      }
    },
    "security-kb-http": {
      "url": "http://localhost:8000",
      "transport": "http"
    }
  }
}
```

### Step 4: Restart Claude Desktop

After updating the configuration:
1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. It should now connect to your HTTP MCP server

## Environment Variables

### For stdio transport (default):
```bash
export MCP_TRANSPORT=stdio  # or don't set it
```

### For HTTP transport:
```bash
export MCP_TRANSPORT=http
export PORT=8000
export HOST=0.0.0.0  # optional, defaults to 0.0.0.0
```

## Railway Deployment

For Railway deployment, the same HTTP transport will work:

```bash
# Railway automatically sets PORT
# Just set the transport
export MCP_TRANSPORT=http
```

## Troubleshooting

### Server not starting:
- Check Neo4j is running: `docker ps | grep neo4j`
- Check environment variables are set
- Check no other service is using port 8000

### Claude Desktop can't connect:
- Verify server is running: `curl http://localhost:8000`
- Check Claude Desktop config file syntax
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for connection errors

### Server running but no response:
- FastMCP might need a moment to fully initialize
- Try accessing different endpoints
- Check server logs for any errors

## Claude Desktop Config File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`