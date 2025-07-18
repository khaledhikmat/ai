from typing import List
from dataclasses import dataclass, field

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

from helpers.providers import get_llm_model

from service.config.envvars import EnvVarsConfigService
from service.crawl.typex import ICrawlService
from service.crawl.craw4ai import AICrawlService
from service.repo.typex import IRepoService
from service.repo.github import GithubRepoService
from service.repo.gitlab import GitlabRepoService

from agent.typex import AgentParameters
from .prompts import SYSTEM_PROMPT

# agent dependecies
@dataclass
class CtxAgentDeps:
    """Dependencies for the CTX agent."""
    crawl_svc: ICrawlService
    repo_svc: IRepoService
    docs: List[str] = field(default_factory=list)

# global variable to hold the agent instance
ctx_agent = Agent(
    get_llm_model(), # get the LLM model based on environment variables
    deps_type=CtxAgentDeps,
    system_prompt=SYSTEM_PROMPT
)
    
# Called from the main app to initialize the agent parameters
async def initialize_agent_params() -> AgentParameters:
    """Get the agent parameters."""
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    crawl_svc = AICrawlService(cfg_svc)
    repo_svc = GithubRepoService(cfg_svc) if cfg_svc.get_repo_type() == "github" else GitlabRepoService(cfg_svc)
    docs = []    

    try:
        if not cfg_svc.get_repo_urls():
            raise ValueError("No repo URLs provided. Please provide a comma-delimited list of repo URLs.")

        md_urls = []
        repo_urls = cfg_svc.get_repo_urls().split(',')
        print(f"Ingesting the following repo URLs: {repo_urls}")
        for repo_url in repo_urls:
            md_urls.extend(await repo_svc.get_md_urls(repo_url.strip()))

        print(f"Crawling the following md URLs: {md_urls}")
        crawl_results = []
        crawl_results.extend(await crawl_svc.crawl(md_urls, max_depth=1, max_concurrent=10))

        # Initialize RAG instance and insert docs
        for i, doc in enumerate(crawl_results):
            url = doc['url']
            md = doc['markdown']
            if not md:
                print(f"Skipping {url} - no markdown content found")
                continue

            print(f"Inserting document from {url} into context doc...")
            docs.append(md)

    except Exception as e:
        print(f"Ingest error occurred: {e}")

    # The crawl service will fetch the documentation and store it in the deps.docs
    deps = CtxAgentDeps(crawl_svc=crawl_svc, repo_svc=repo_svc, docs=docs)
    return AgentParameters(
        title="CTX Agent",
        description="An agent that answers questions about contextual documentation.",
        deps=deps,
        agent=ctx_agent
    )

# Called from the main app to finalize the agent parameters
async def finalize_agent_params(parameters: AgentParameters) -> None:
    """Finalize the agent dependencies."""
    parameters.deps.crawl_svc.finalize()
    parameters.deps.repo_svc.finalize()

@ctx_agent.system_prompt
async def inject_docs(ctx: RunContext[CtxAgentDeps]) -> str:
    return "\n\n".join(ctx.deps.docs)
