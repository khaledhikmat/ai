# AI Project Structure

A collection of MCP servers, AI agents and services that experiment with different AI tools and strategies using a unified Streamlit interface.

## Architecture Overview

The project follows a modular architecture with clear separation between agents, services, and the presentation layer:

```
ai/
├── agent/          # Agent implementations
├── service/        # Core service abstractions
├── mcp_servers/    # MCP server implementations
├── helpers/        # Utility functions
├── app.py          # Main Streamlit application
├── cli.py          # Command-line interface router
├── mcp_server.py   # MCP server runner
└── test.py         # Test utilities
```

## Service Layer Abstraction

The `service/` directory contains modular, reusable services that are abstracted through interfaces:

### Core Services

- **Config Service** (`service/config/`): Environment variable management
- **Repository Service** (`service/repo/`): GitHub/GitLab repository integration
- **Crawler Service** (`service/crawl/`): Web content crawling using Crawl4AI
- **Chunker Service** (`service/chunker/`): Document chunking (semantic, simple)
- **Embedder Service** (`service/embedder/`): Text embedding generation
- **RAG Service** (`service/rag/`): Multiple RAG strategies (LightRAG, GraphRAG, Naive)
- **Graph Service** (`service/graph/`): Graph database integration (Neo4j, Graphiti)
- **Security Service** (`service/security/`): Security knowledge base operations with Neo4j

### Service Abstraction Pattern

Services follow a consistent pattern using TypeX interfaces:
- Each service has a `typex.py` file defining the interface
- Concrete implementations provide specific functionality
- Services are injected as dependencies into agents

Example service interface pattern:
```python
# service/rag/typex.py
class IRAGService(ABC):
    async def query(self, question: str) -> str
    async def finalize(self) -> None
```

## Agent Architecture

The project supports three main agent types, each with their own specialized functionality:

### Agent Types

1. **DOC Agent** (`agent/doc/`): Documentation Q&A using RAG
2. **CTX Agent** (`agent/ctx/`): Context-based documentation queries
3. **INH Agent** (`agent/inheritance/`): Family inheritance knowledge graphs

### Agent Structure

Each agent follows a consistent pattern:
```
agent/{type}/
├── agent.py      # Agent implementation and dependencies
├── cli.py        # Command-line interface
└── prompts.py    # System prompts
```

### Agent Dependencies

Agents use dependency injection through the `AgentParameters` dataclass:

```python
@dataclass
class DocAgentDeps:
    ragsvc: IRAGService

# Agent initialization
async def initialize_agent_params() -> AgentParameters:
    cfg_svc = EnvVarsConfigService()
    crawl_svc = AICrawlService(cfg_svc)
    rag_svc = LightRAGService(cfg_svc, crawl_svc)
    deps = DocAgentDeps(ragsvc=rag_svc)
    return AgentParameters(
        title="Doc Agent",
        description="An agent that answers questions about documentation.",
        deps=deps,
        agent=doc_agent
    )
```

## Unified Streamlit Interface

The main Streamlit application (`app.py`) provides a unified interface that can run any agent type through a common pattern:

### Agent Registration

Agents are registered through initialization and finalization function mappings:

```python
agent_init_fns: AGENT_INIT_FNS = {
    "doc": init_doc_agent,
    "ctx": init_ctx_agent,
    "inh": init_inh_agent,
}

agent_fin_fns: AGENT_FIN_FNS = {
    "doc": fin_doc_agent,
    "ctx": fin_ctx_agent,
    "inh": fin_inh_agent,
}
```

### Runtime Agent Selection

Agents are selected at runtime using environment variables:

```bash
export AGENT_TYPE=doc
export AGENT_RAG_STRATEGY=lr
streamlit run app.py
```

### Common Streamlit Flow

1. **Agent Initialization**: Load agent-specific dependencies and configuration
2. **Session Management**: Maintain conversation history and agent state
3. **Streaming Interface**: Provide real-time response streaming
4. **Message Display**: Handle different message types (user, assistant, tool calls)
5. **Agent Finalization**: Clean up resources when session ends

### Key Features

- **Streaming Responses**: Real-time text streaming using Pydantic AI
- **Message History**: Persistent conversation state across interactions
- **Tool Integration**: Support for function calling and tool responses
- **Error Handling**: Graceful error management and user feedback

## CLI Integration

The command-line interface (`cli.py`) routes commands to agent-specific CLI processors:

```python
cli_processors: Dict[str, Callable[..., Awaitable[None]]] = {
    "doc": doc_agent_cli,
    "inh": inh_agent_cli,
}
```

Usage pattern:
```bash
python3 cli.py <agent-type> <command> <args>
python3 cli.py doc ingest_lr https://github.com/user/repo
```

## LLM Provider Support

The project supports multiple LLM providers through the `helpers/providers.py` module:
- **OpenAI**: Primary provider with optimal performance
- **Gemini**: Alternative provider with some performance considerations
- **Ollama**: Local model support for privacy-focused deployments

## Data Flow

1. **Ingestion**: CLI tools ingest data from repositories/sources into RAG systems
2. **Service Layer**: Abstracted services handle crawling, chunking, embedding, and storage
3. **Agent Layer**: Agents use injected services to process user queries
4. **Streamlit UI**: Unified interface presents all agents through a common chat interface

## MCP Server Architecture

The project includes Model Context Protocol (MCP) servers that follow the same delegation pattern as agents:

### MCP Server Structure

MCP servers are organized in the `mcp_servers/` directory with the following pattern:
```
mcp_servers/
├── typex.py                    # MCP server interface definitions
├── {server_type}/
│   ├── server.py              # Server implementation with delegation
│   └── __init__.py
└── __init__.py
```

### MCP Server Delegation Pattern

Similar to agents, MCP servers use dependency injection and delegation:

```python
@dataclass
class SecurityMCPDeps:
    security_service: Neo4jSecurityKnowledgeBaseService

async def initialize_mcp_params() -> MCPServerParameters:
    config_service = EnvVarsConfigService()
    security_service = Neo4jSecurityKnowledgeBaseService(config_service)
    await security_service.initialize()
    
    deps = SecurityMCPDeps(security_service=security_service)
    mcp = fastmcp.FastMCP("Security Knowledge Base")
    
    # Register resources and tools using deps.security_service
    
    return MCPServerParameters(
        name="Security Knowledge Base",
        description="MCP server for security incident management",
        deps=deps,
        server=mcp
    )
```

### Unified MCP Server Runner

The root `mcp_server.py` provides centralized MCP server management:

```python
mcp_init_fns: MCP_INIT_FNS = {
    "security": init_security_mcp,
    # Add more MCP servers here
}
```

Usage:
```bash
# From project root
export MCP_TYPE=security
python mcp_server.py

# Or directly
python mcp_server.py security
```

### Key Benefits

- **Consistent Architecture**: Same delegation pattern as agents and CLI
- **Service Reuse**: MCP servers can use any service from the service layer
- **Module Loading**: No Python path issues when running from project root
- **Centralized Management**: Single entry point for all MCP servers
- **Easy Extension**: Simple pattern to add new MCP server types

This architecture provides a clean separation of concerns, making it easy to add new agents, services, MCP servers, or modify the presentation layer independently.