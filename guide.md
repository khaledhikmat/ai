# AI Project Source Code Guide

## Overview

This is a comprehensive guide to understanding the AI project codebase, a modular collection of MCP servers, AI agents, and services built using a unified Streamlit interface. The project follows clean architecture principles with clear separation of concerns and dependency injection patterns.

## Project Architecture

### High-Level Structure

```
ai/
├── agent/           # Agent implementations with dependency injection
├── service/         # Core service abstractions (Protocol-based interfaces)
├── mcp_servers/     # Model Context Protocol server implementations
├── helpers/         # Utility functions and providers
├── app.py           # Main Streamlit application
├── cli.py           # Command-line interface router
├── mcp_server.py    # MCP server runner
└── requirements.txt # Python dependencies
```

### Core Design Principles

1. **Dependency Injection**: Services are injected into agents and MCP servers
2. **Protocol-Based Interfaces**: All services implement Protocol interfaces (typex.py)
3. **Delegation Pattern**: Unified entry points delegate to specific implementations
4. **Modular Design**: Clear separation between agents, services, and presentation layer

## Service Layer (`service/`)

The service layer provides the core business logic through Protocol-based interfaces, enabling easy testing and multiple implementations.

### Service Architecture Pattern

Each service follows this consistent structure:

```
service/{service_name}/
├── typex.py          # Protocol interface definition
├── {implementation}.py # Concrete implementations
└── __init__.py
```

### Core Services

#### Configuration Service (`service/config/`)

**Interface**: `IConfigService` (`typex.py:22-136`)
**Implementation**: `EnvVarsConfigService` (`envvars.py`)

Centralizes environment variable management with strong typing:

```python
class IConfigService(Protocol):
    def get_repo_type(self) -> str: ...
    def get_neo4j_uri(self) -> str: ...
    def get_llm_provider(self) -> str: ...
    def get_chunking_config(self) -> ChunkingConfig: ...
```

#### Repository Service (`service/repo/`)

**Interface**: `IRepoService` (`typex.py`)
**Implementations**: `GitHubRepoService`, `GitLabRepoService`

Abstracts repository operations:

```python
class IRepoService(Protocol):
    async def get_file_tree(self) -> Dict[str, Any]: ...
    async def get_file_content(self, file_path: str) -> str: ...
```

#### Crawler Service (`service/crawl/`)

**Interface**: `ICrawlService` (`typex.py:4-12`)
**Implementation**: `AICrawlService` (uses Crawl4AI)

Web content crawling with configurable depth and concurrency:

```python
class ICrawlService(Protocol):
    async def crawl(self, urls, max_depth, max_concurrent) -> List[Dict[str,Any]]: ...
```

#### RAG Service (`service/rag/`)

**Interface**: `IRAGService` (`typex.py:15-34`)
**Implementations**: `LightRAGService`, `GraphRAGService`, `NaiveRAGService`

Retrieval-Augmented Generation with multiple strategies:

```python
class IRAGService(Protocol):
    async def ingest_md_urls(self, urls: str, progress_callback: Optional[callable] = None) -> List[IngestionResult]: ...
    async def retrieve(query: str) -> str: ...
```

#### Graph Service (`service/graph/`)

**Interface**: `IGraphService` (`typex.py`)
**Implementations**: `Neo4jGraphService`, `GraphitiGraphService`

Graph database operations for knowledge graphs and relationships.

## Agent Architecture (`agent/`)

Agents implement AI-powered functionality using dependency injection and the Pydantic AI framework.

### Agent Structure Pattern

```
agent/{agent_type}/
├── agent.py         # Agent implementation with dependencies
├── cli.py           # Command-line interface
├── prompts.py       # System prompts
└── __init__.py
```

### Agent Types

1. **DOC Agent** (`agent/doc/`): Documentation Q&A using RAG
2. **CTX Agent** (`agent/ctx/`): Context-based documentation queries  
3. **INH Agent** (`agent/inheritance/`): Family inheritance knowledge graphs
4. **INC Agent** (`agent/incidents/`): Security incident management

### Agent Implementation Pattern

**Dependencies Definition** (`agent/doc/agent.py:17-22`):
```python
@dataclass
class DocAgentDeps:
    """Dependencies for the DOC agent."""
    ragsvc: IRAGService
```

**Agent Creation** (`agent/doc/agent.py:24-28`):
```python
doc_agent = Agent(
    get_llm_model(),
    deps_type=DocAgentDeps,
    system_prompt=SYSTEM_PROMPT
)
```

**Dependency Injection** (`agent/doc/agent.py:31-44`):
```python
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

**Tool Integration** (`agent/doc/agent.py:51-62`):
```python
@doc_agent.tool
async def retrieve(context: RunContext[DocAgentDeps], search_query: str) -> str:
    return await context.deps.ragsvc.retrieve(search_query)
```

## MCP Server Architecture (`mcp_servers/`)

MCP servers follow the same delegation pattern, providing Model Context Protocol interfaces.

### MCP Structure Pattern

```
mcp_servers/
├── typex.py                # MCP server interface definitions
├── {server_type}/
│   ├── server.py          # Server implementation with delegation
│   └── __init__.py
```

### MCP Server Parameters (`mcp_servers/typex.py:6-12`)

```python
@dataclass
class MCPServerParameters:
    name: str
    description: str
    deps: Any = field(default=None, repr=False)
    server: Any = field(default=None, repr=False)  # fastmcp.FastMCP
```

### Unified MCP Runner (`mcp_server.py`)

Central runner supporting both stdio and HTTP transports:

```python
mcp_init_fns: MCP_INIT_FNS = {
    "inc": init_inc_mcp,
    # Add more MCP servers here
}

def main(mcp_type: str):
    mcp_params = mcp_init_fns[mcp_type]()
    # Run with stdio or HTTP transport based on environment
```

## Streamlit Integration (`app.py`)

### Unified Agent Interface

The Streamlit app provides a single interface that can run any agent type through runtime configuration:

**Agent Registration** (`app.py:56-68`):
```python
agent_init_fns: AGENT_INIT_FNS = {
    "doc": init_doc_agent,
    "ctx": init_ctx_agent,
    "inh": init_inh_agent,
    "sec": init_inc_agent,
}
```

**Runtime Selection**:
```bash
export AGENT_TYPE=doc
export AGENT_RAG_STRATEGY=lr
streamlit run app.py
```

### Streaming Integration (`app.py:45-54`)

Real-time response streaming using Pydantic AI:

```python
async def run_agent_with_streaming(agent: Agent, user_input):
    async with agent.run_stream(
        user_input, deps=st.session_state.agent_deps, message_history=st.session_state.messages
    ) as result:
        async for message in result.stream_text(delta=True):  
            yield message
```

## CLI Integration (`cli.py`)

Command-line router that delegates to agent-specific CLI processors:

```python
cli_processors: Dict[str, Callable[..., Awaitable[None]]] = {
    "doc": doc_agent_cli,
    "inh": inh_agent_cli,
}

# Usage: python3 cli.py doc ingest_lr https://github.com/user/repo
```

## LLM Provider Support (`helpers/providers.py`)

Flexible provider configuration supporting multiple LLM backends:

### Provider Functions (`helpers/providers.py:16-31`)

```python
def get_llm_model(model_choice: Optional[str] = None) -> OpenAIModel:
    llm_choice = model_choice or os.getenv('LLM_CHOICE', 'gpt-4-turbo-preview')
    base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
    api_key = os.getenv('LLM_API_KEY', 'ollama')
    
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    return OpenAIModel(llm_choice, provider=provider)
```

### Supported Providers

- **OpenAI**: Primary provider with optimal performance
- **Local Models**: Ollama support for privacy-focused deployments
- **Custom Endpoints**: Any OpenAI-compatible API

## Key Technologies

### Core Dependencies (`requirements.txt`)

- **pydantic_ai**: Agent framework with streaming support
- **streamlit**: Web UI framework
- **lightrag-hku**: Advanced RAG implementation
- **neo4j**: Graph database for knowledge graphs
- **Crawl4AI**: Web content extraction
- **fastmcp**: Model Context Protocol server framework
- **google-genai**: Gemini AI integration
- **sentence_transformers**: Embedding generation

### Data Flow

1. **Configuration**: Environment variables loaded via `IConfigService`
2. **Ingestion**: CLI tools crawl and process data via `ICrawlService` 
3. **Storage**: Data stored in RAG systems (`IRAGService`) and graph databases (`IGraphService`)
4. **Query Processing**: Agents use injected services to process user queries
5. **Response Generation**: Pydantic AI agents stream responses via Streamlit UI

## Implementation Patterns

### Adding a New Service

1. Define Protocol interface in `service/{name}/typex.py`
2. Implement concrete class in `service/{name}/{implementation}.py`
3. Use dependency injection to provide service to agents

### Adding a New Agent

1. Create agent directory: `agent/{name}/`
2. Define dependencies dataclass
3. Implement agent with `@agent.tool` decorators
4. Add initialization/finalization functions
5. Register in `app.py` and `cli.py`

### Adding a New MCP Server

1. Create server directory: `mcp_servers/{name}/`
2. Implement server with dependencies
3. Register in `mcp_server.py`
4. Configure transport (stdio/HTTP) via environment

## Environment Configuration

Key environment variables for different components:

```bash
# Agent Selection
AGENT_TYPE=doc                    # Agent type selection
AGENT_RAG_STRATEGY=lr            # RAG strategy

# LLM Configuration  
LLM_PROVIDER=openai              # Provider type
LLM_CHOICE=gpt-4-turbo-preview   # Model selection
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_key_here

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# MCP Server Configuration
MCP_TYPE=inc                     # MCP server type
MCP_TRANSPORT=stdio              # Transport method (stdio/http)
PORT=8000                        # HTTP port (if using HTTP transport)
```

This architecture provides excellent separation of concerns, making it easy to extend functionality, swap implementations, and maintain consistent patterns across the codebase.