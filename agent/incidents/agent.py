import os
from dataclasses import dataclass
import asyncio
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

from helpers.providers import get_llm_model

from agent.typex import AgentParameters
from .prompts import SYSTEM_PROMPT

@dataclass
class SecurityAgentDeps:
    """Dependencies for the Security agent."""
    pass

# Global variable to hold the agent instance
server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
server = MCPServerStreamableHTTP(server_url)
security_agent = Agent(
    get_llm_model(),
    deps_type=SecurityAgentDeps,
    system_prompt=SYSTEM_PROMPT,
    toolsets=[server]
)

async def initialize_agent_params() -> AgentParameters:
    """Get the agent parameters."""
    await asyncio.sleep(0.1)
    # Initialize services
    deps = SecurityAgentDeps()
    return AgentParameters(
        title="Security AI Agent using MCP Server",
        description="An agent that answers questions about security knowledge base using MCP Server tooling.",
        deps=deps,
        agent=security_agent
    )

async def finalize_agent_params(parameters: Optional[AgentParameters] = None) -> None:
    await asyncio.sleep(0.1)
