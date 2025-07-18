import sys
import argparse
from typing import Dict, Callable, Awaitable
from dotenv import load_dotenv

load_dotenv()

def ingest_progress_callback(ingestor: str, current: int, total: int):
    print(f"Ingest Progress: {ingestor} - {current}/{total} documents processed")

# define `ingest_naive` as a command processor to ingest into a RAG 
# using naive from a list of repository URLs.
async def ingest(repo_urls: str) -> None:
    try:
        raise ValueError("Not supported yet.")
    except Exception as e:
        print(f"Ingest error occurred: {e}")

# define a command processors mapping where each key is a command name
# and the value is an async function that performs the command. 
# the processor is a callable function that takes variant 
# input arguments, returns None and must be awaited. 
processors: Dict[str, Callable[..., Awaitable [None]]] = {
    "ingest": ingest,
}

async def main():
    parser = argparse.ArgumentParser(description="CLI Processor to support CTX agent.")
    parser.add_argument("proc_name", help="processor command")
    parser.add_argument("repo_urls", help="comma-delimited repo URLs to iterate through looking for .md URLs")
    args = parser.parse_args()

    if not args.proc_name:
        print("No proc name is provided. Please provide a processor i.e. ingest.")
        sys.exit(1)

    if args.proc_name not in processors:
        print(f"Unknown command: {args.proc_name}. Available commands: {', '.join(processors.keys())}")
        sys.exit(1)

    if not args.repo_urls:
        print("No repo URLs provided. Please provide a comma-delimited list of repo URLs.")
        sys.exit(1)

    await processors[args.proc_name](args.repo_urls)
