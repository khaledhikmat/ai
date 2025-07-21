*Disclaimer: Picked up code and ideas from: [https://github.com/coleam00/ottomator-agents.git](https://github.com/coleam00/ottomator-agents.git).*

A collection of MCP servers, AI agents and services to experiment with different AI tools and strategies.

Please refer to [tasks](./tasks.md) for a list of pending tasks and issues and refer to [guide](./guide.md) for a conceptual understanding of source code structure.  

---

## Agents

The following agents are available:

### DOC Agent

This is a helpful assistant that answers questions about system documentation based on provided Markdown URLs.

The ingest process (generating RAG docs) supports reading repo URLs from a URL list separated by a comma. Repo URLs list can be for Gitlab or Github repositories (and they can be mixed). The ingestor walks through the repository looking for `.md` URLs. The `.md` files content will be source of the documenation knowledge base.

Query documentation knowledge base using natural language and get context-rich answers. Example questions:
- Which language is the video-sureveillance backend is written in?
- Can you describe the video-sureveillance architecture?

The following are available RAG strategies:
- `nv`: Naive RAG
- `lr`: Light RAG
- `gr`: Graphiti RAG 

TBA (Mermaid to show how the build and agent run processes work)

### CTX Agent

This is a helpful assistant that answers questions about system documentation found on provided Markdown URLs.

There is no ingestion process! The agent automatically fetches the Markdown URLs from the repo and provides them as a context to the LLM so it can answer questions based on the provided context.

The disadvantage of this approach is that we are using a big context for every question. The advantage, of course, is that there is no need for a RAG system.

TBA (Mermaid to show how the build and agent run processes work)

### INH Agent

This is a helpful assistant that answers questions about family inheritance based on a knowledge graph.

The ingest process (generating knowledge graph) supports reading from different data sources: JSON files or database. Please refer to a samle JSON files in [sample data](./sample-data/).

Query inheritance knowledge base documentation using natural language and get context-rich answers. Example questions:
- How many properties are there in <country>?
- How many inheritors of <person_name>?

The following are available RAG strategies:
- `tools`: Use function calling to retrieve context data 

TBA (Mermaid to show how the build and agent run processes work)

### INC Agent

This is a helpful assistant that answers questions about enterprise security incidents using an MCP Server.

There is no ingestion process for the agent! But the MCP Server has its own ingetion or initialization code that seeds data into its database.

TBA (Mermaid to show how the build and agent run processes work)

## MCP Servers

The following MCP Servers are available:

### Security Incidents

TBA

## Prerequisites

- Python 3.11+
- OpenAI API key (for embeddings and LLM-powered search)
- GeminiAI API key (for LLM-powered search)
- Dependencies in `requirements.txt`

---

## Installation

1. **Install dependencies:**

```bash
python3 -m venv venv
source venv/bin/activate 
pip3 install -r requirements.txt
playwright install
```

2. **Set up environment variables:**

- Copy `.env.example` to `.env`
- Edit `.env` with your API keys and preferences.

3. **Start Neo4j container:**

*Optional: needed if you are planning to use Neo4J*

- Make sure you have neo4j folder in $HOME.
- Check to make sure that the container is not already running:

```bash
docker ps
```

- Stop the container (optional):

```bash
docker stop neo4j
```

- Remove the container (optional):

```bash
docker rm neo4j
```

- Delete `neo4j` folder subfolders (i.e. `data` and `logs`) and re-create them to remove all data (optional).

- Start the container:

```bash
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -d \
  -e NEO4J_AUTH="neo4j/admin4neo4j" \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  neo4j:latest
```

- Access Neo4j dashboard and connect using the credentials provided i.e. `neo4j/admin4neo4j`:

```bash
http://localhost:7474
```

---

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
    "sec": init_security_mcp,
    "news": init_newserver_mcp,  # Add here
}
```

3. Run it:
```bash
python mcp_server.py newserver
```

---

## LightRAG LLM Support

Normally, LightRAG works out of the box with OpenAI and it seems it is a good option. But if you don't want to use OpenAI or any other Cloud-based models, the other option is to use Ollama as it has out-of-the-box support in LightRAG. This project supports `openai`, `gemini` and `ollama`. 

Please note that the `Gemini` support is not totally native. I noticed a huge performance degredation when using Gemini. Defintely the best option is OpenAI.

To activate OpenAI, please set the following env vars:
- `LLM_TYPE=openai`
- `LLM_MODEL_NAME=gpt-4o-mini`
- `OPENAI_API_KEY=<openai-api-key>`

To activate Gemini, please set the following env vars:
- `LLM_TYPE=gemini`
- `LLM_MODEL_NAME=gemini-1.5-flash`
- `GEMINI_API_KEY=<gemini-api-key>`

To activate Ollama, please set the following env vars:
- `LLM_TYPE=ollama`
- `LLM_MODEL_NAME=qwen2.5-coder:7b`

**Please note** if you are running Ollama, you must download and install Ollam locally and then run it:
- On Unix:
    - `curl -fsSL https://ollama.com/install.sh | sh`
- On MacOS & Windows:
    - Visit https://ollama.com/download
- `ollama pull qwen2.5-coder:7b`
- `ollama pull bge-m3:latest`
- `ollama serve` # On Mac OS, the agent starts automatically
- To confirm models are pulled properly, open up a new terminal and do: `ollama list`.
- To confirm Ollama is running: `curl http://localhost:11434/api/tags`
- Ollama runs the models locally and hence it requires a lot of processing power. I was not able to make it work well. My Mac (16 GB) was heating up quite a bit.

---

## TEST commands

This module contains different test processors to exercise isolated aspects of the solution. Every TEST processor can be invoked from `test.py`. Here is the general format:

```bash
python3 test.py <test-name> <arg1>
# examples:
## repo service:
python3 test.py test_repo https://github.com/khaledhikmat/vs-go
## chunker service:
python3 test.py test_chunker xxx
## graphiti service:
python3 test.py test_graphiti xxx
## neo4j service:
python3 test.py test_neo4j xxx
```

---

## Agent CLI commands

Every agent type (i.e. `doc`, `inh`, etc) has its own CLI. However, the root `cli.py` routes the CLI processing to the different agent type specific CLI. Here is the general format:

```bash
python3 cli.py <agent-type> <proc-name> <extra-args>
```

The most important CLI command that each agent type must support is `ingest` command: 

### DOC Agent

The following are some examples of `doc` agent ingest commands:

```bash
python3 cli.py doc ingest <rag-strategy> <repo_url1,repo_url2>

## ingest using light rag
python3 cli.py doc ingest_lr <repo_url1,repo_url2>
pythin3 cli.py doc ingest_lr https://github.com/khaledhikmat/vs-go
## ingest using graph rag
python3 cli.py doc ingest_gr <repo_url1,repo_url2>
## ingest using naive rag
python3 cli.py doc ingest_nv <repo_url1,repo_url2>
```

### CTX Agent

The `ctx` agent does not support any CLI commands.

### INH Agent

The following are some examples of `inh` agent ingest commands:

```bash
python3 cli.py inh ingest <data-source>

## ingest using json data source
python3 cli.py inh ingest json
```

The `json` data source assumes JSON files exist in `./data` folder named: `persons.json` and `properties.json`. Please use the [sample files](./sample-data/) to build your own. 

### INC Agent

The `inc` agent does not support any CLI commands.

---

## Running the Agent

The root `app.py` routes the APP processing to the different agent type specific APP. Here is the general format:

```bash
export AGENT_TYPE=<agent-type>
export AGENT_RAG_STRATEGY=<strategy-type>
streamlit run app.py

# examples:
export AGENT_TYPE=doc
export AGENT_RAG_STRATEGY=lr
streamlit run app.py
export AGENT_TYPE=ctx
export AGENT_RAG_STRATEGY=tools
streamlit run app.py
export AGENT_TYPE=inh
export AGENT_RAG_STRATEGY=tools
streamlit run app.py
export AGENT_TYPE=inc
streamlit run app.py
```

*It might be better to provide a drop-down widget to select the different agent types.*

`app.py` expects each agent to expose agent [initializer](./agent/typex.py) and [finalizer](./agent/typex.py) functions.  

The interface will be available at [http://localhost:8501](http://localhost:8501)

---

## MCP CLI commands

Every mcp server type (i.e. `inc`, etc) has its own CLI. However, the root `mcp_cli.py` routes the CLI processing to the different mcp type specific CLI. Here is the general format:

```bash
python3 mcp_cli.py <mcp-server-type> <proc-name> <extra-args>
```

The most important CLI command that each agent type must support is `ingest` command: 

### Security Incidents MCP Server

```bash
## ingest using json random data
python3 mcp_cli.py inc ingest
```

This is to seed data into the MCP Server database.

---

## Running the MCP Server

```bash
# From project root directory
python3 mcp_server.py inc

# Or using environment variable
export MCP_TYPE=inc
python3 mcp_server.py
```

## Testing the MCP Server Locally

Unfortuantely it has been very difficult to get the MCP Server to test. I was only able to test locally using Clause desktop with the following configuration:

```json
{
  "mcpServers": {
    "security-kb": {
      "command": "/Users/khaled/github/ai/venv/bin/python",
      "args": ["/Users/khaled/github/ai/mcp_server.py", "security"],
      "cwd": "/Users/khaled/github/ai",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "admin4neo4j",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

This uses `stdio` transport and forces Claude to use the `venv` in my project and it works fine. 

Then I added support for `http` transport and I was able to launch it locally:

```bash
export MCP_TYPE=inc
python3 mcp_server.py
```

But Claude desktop reported a parse erron on the configuration file when I added `http` transport:

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

Switched Copilot to agent mode and requested tools. Added a new MCP Server using HTTP transport and selected user settings:

```json
"mcp": {
        "servers": {
            "sec-inc-kb": {
                "url": "http://localhost:8000/mcp/"
            }
        }
    }
```

Initially it did not work because I had the URL set as: `http://localhost:8000/mcp` (without the end slash). Eventually it worked with the end forward slash.

Switch Copilot to Agent Mode -> Tools -> Add More Tools -> Add MCP Server -> HTTP Server.

Then use `/tools` to make requests to the MCP server and interact with the security incident data. Then ask a question:

```
Show 10 incidents
```

Yay...this woked!!!

## Deploying the MCP Server to Railway

BTW...attempts to deploy Neo4J to Railway did not work well. The mixture of bolt and http ports confused the browser. Eventually I gave up on Railway to deploy my MCP Server. 

---

