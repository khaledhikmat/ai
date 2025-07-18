import sys
import argparse
from typing import Dict, Callable, Awaitable
from dotenv import load_dotenv

from service.config.envvars import EnvVarsConfigService
from service.repo.github import GithubRepoService
from service.repo.gitlab import GitlabRepoService
from service.crawl.craw4ai import AICrawlService
from service.chunker.semantic import SemanticChunkerService
from service.graph.graphiti import GraphitiGraphService
from service.rag.naive import NaiveRAGService
from service.rag.lightrag import LightRAGService
from service.rag.graphrag import GraphRAGService

load_dotenv()

def ingest_progress_callback(ingestor: str, current: int, total: int):
    print(f"Ingest Progress: {ingestor} - {current}/{total} documents processed")

# define `ingest_naive` as a command processor to ingest into a RAG 
# using naive from a list of repository URLs.
async def ingest_naive(repo_urls: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    repo_svc = GithubRepoService(cfg_svc) if cfg_svc.get_repo_type() == "github" else GitlabRepoService(cfg_svc)
    crawl_svc = AICrawlService(cfg_svc)
    chunker_svc = SemanticChunkerService(cfg_svc)
    rag_svc = NaiveRAGService(cfg_svc, crawl_svc, chunker_svc)

    try:
        raise ValueError("Not supported yet.")
    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        repo_svc.finalize()
        crawl_svc.finalize()
        chunker_svc.finalize()
        rag_svc.finalize()

# define `ingest_lightrag` as a command processor to ingest into a RAG 
# using LightRAG from a list of repository URLs.
async def ingest_lightrag(repo_urls: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    repo_svc = GithubRepoService(cfg_svc) if cfg_svc.get_repo_type() == "github" else GitlabRepoService(cfg_svc)
    crawl_svc = AICrawlService(cfg_svc)
    rag_svc = LightRAGService(cfg_svc, crawl_svc)

    try:
        if not repo_urls:
            raise ValueError("No repo URLs provided. Please provide a comma-delimited list of repo URLs.")

        md_urls = []
        repo_urls = repo_urls.split(',')
        print(f"Received the following repo URLs: {repo_urls}")
        for repo_url in repo_urls:
            md_urls.extend(await repo_svc.get_md_urls(repo_url.strip()))

        print(f"Crawling the following md URLs: {md_urls}")
        result = await rag_svc.ingest_md_urls(md_urls, ingest_progress_callback) 
        print(f"Successfully added docs to the configured RAG service: {result}")
    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        repo_svc.finalize()
        crawl_svc.finalize()
        rag_svc.finalize()

# define `ingest_graphrag` as a command processor to ingest into a RAG 
# using Graphrag from a list of repository URLs.
async def ingest_graphrag(repo_urls: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    repo_svc = GithubRepoService(cfg_svc) if cfg_svc.get_repo_type() == "github" else GitlabRepoService(cfg_svc)
    crawl_svc = AICrawlService(cfg_svc)
    chunker_svc = SemanticChunkerService(cfg_svc)
    graph_svc = GraphitiGraphService(cfg_svc)
    rag_svc = GraphRAGService(cfg_svc, crawl_svc, chunker_svc, graph_svc)

    try:
        if not repo_urls:
            raise ValueError("No repo URLs provided. Please provide a comma-delimited list of repo URLs.")

        md_urls = []
        repo_urls = repo_urls.split(',')
        print(f"Received the following repo URLs: {repo_urls}")
        for repo_url in repo_urls:
            md_urls.extend(await repo_svc.get_md_urls(repo_url.strip()))

        print(f"Crawling the following md URLs: {md_urls}")
        result = await rag_svc.ingest_md_urls(md_urls, ingest_progress_callback) 
        print(f"Successfully added docs to the configured RAG service: {result}")
    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        repo_svc.finalize()
        crawl_svc.finalize()
        chunker_svc.finalize()
        await graph_svc.finalize()
        rag_svc.finalize()

# define a command processors mapping where each key is a command name
# and the value is an async function that performs the command. 
# the processor is a callable function that takes variant 
# input arguments, returns None and must be awaited. 
processors: Dict[str, Callable[..., Awaitable [None]]] = {
    "ingest_nv": ingest_naive,
    "ingest_lr": ingest_lightrag,
    "ingest_gr": ingest_graphrag,
}

async def main():
    parser = argparse.ArgumentParser(description="CLI Processor to support DOC agent.")
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
