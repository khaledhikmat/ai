from typing import Callable, Awaitable
from dataclasses import dataclass, field

from pydantic_ai.agent import Agent

@dataclass
class AgentParameters:
    """Configuration for the agent."""
    title: str
    description: str
    deps: object = field(default=None, repr=False)
    agent: Agent = field(default=None, repr=False)

# Type aliases for agent initialization and finalization functions
AGENT_INIT_FNS = dict[str, Callable[[], Awaitable[AgentParameters]]]
AGENT_FIN_FNS = dict[str, Callable[[AgentParameters], Awaitable[None]]]

