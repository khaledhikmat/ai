"""
Command-line utility to route commands to different CLI processors.
"""
import sys
import asyncio
from typing import Dict, Callable, Awaitable
from dotenv import load_dotenv

from agent.doc.cli import main as doc_agent_cli
from agent.inheritance.cli import main as inh_agent_cli

load_dotenv()

# sub-cli processors are defined here.
cli_processors: Dict[str, Callable[..., Awaitable [None]]] = {
    "doc": doc_agent_cli,
    "inh": inh_agent_cli,
}

async def main(cli_name: str):
    if not cli_name:
        print("No cli name is provided. Please provide a processor i.e. build.")
        sys.exit(1)

    if cli_name not in cli_processors:
        print(f"Unknown command: {cli_name}. Available commands: {', '.join(cli_processors.keys())}")
        sys.exit(1)

    # Pass the extra arguments to the sub-cli processor
    await cli_processors[cli_name](sys.argv[2:])

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))  # Pass 1st first command-line argument to main
