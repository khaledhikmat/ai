import sys
import argparse
from typing import Dict, Callable, Awaitable
from dotenv import load_dotenv

load_dotenv()

def ingest_progress_callback(ingestor: str, current: int, total: int):
    print(f"Ingest Progress: {ingestor} - {current}/{total} documents processed")

async def ingest() -> None:
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
    parser = argparse.ArgumentParser(description="CLI Processor to support INC agent.")
    parser.add_argument("proc_name", help="processor command")
    args = parser.parse_args()

    if not args.proc_name:
        print("No proc name is provided. Please provide a processor i.e. ingest.")
        sys.exit(1)

    if args.proc_name not in processors:
        print(f"Unknown command: {args.proc_name}. Available commands: {', '.join(processors.keys())}")
        sys.exit(1)

    await processors[args.proc_name]()
