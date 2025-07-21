"""
CLI for the Security Agent
"""

import asyncio
import click
from pydantic_ai import RunContext

from .agent_mcp_client import initialize_agent_params, finalize_agent_params

@click.command()
@click.option("--query", "-q", required=True, help="Security query to process")
async def run_security_agent(query: str):
    """Run the security agent with a query."""
    try:
        # Initialize agent
        agent_params = await initialize_agent_params()
        print(f"🛡️  {agent_params.title}")
        print(f"📋 {agent_params.description}")
        print("=" * 50)
        
        # Run the agent with the query
        result = await agent_params.agent.run(
            query,
            deps=agent_params.deps
        )
        
        print(f"\n🤖 Agent Response:")
        print(result.data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if 'agent_params' in locals():
            await finalize_agent_params(agent_params)


if __name__ == "__main__":
    asyncio.run(run_security_agent())