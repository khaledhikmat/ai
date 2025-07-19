"""
Command-line utility to perform test commands.
"""
import sys
import asyncio
import argparse
import json
from typing import Dict, Callable, Awaitable, Optional, Any, List
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from graphiti_core.nodes import EpisodeType        

from service.config.envvars import EnvVarsConfigService
from service.repo.github import GithubRepoService
from service.repo.gitlab import GitlabRepoService
from service.crawl.craw4ai import AICrawlService
from service.chunker.semantic import SemanticChunkerService
from service.chunker.simple import SimpleChunkerService
from service.graph.graphiti import GraphitiGraphService
from service.graph.neo4j import Neo4jGraphService
from service.rag.naive import NaiveRAGService
from service.rag.lightrag import LightRAGService
from service.rag.graphrag import GraphRAGService

load_dotenv()

def ingest_progress_callback(ingestor: str, current: int, total: int):
    print(f"Ingest Progress: {ingestor} - {current}/{total} documents processed")

# define `repo_svc_tester` as a command processor to test repo service.
async def repo_svc_tester(repo_urls: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    repo_svc = GithubRepoService(cfg_svc) if cfg_svc.get_repo_type() == "github" else GitlabRepoService(cfg_svc)

    try:
        repo_urls = repo_urls.split(',')
        if not repo_urls:
            raise ValueError("No repo URLs provided. Please provide a comma-delimited list of repo URLs.")

        print(f"Received the following repo URLs: {repo_urls}")
        md_urls = []
        for repo_url in repo_urls:
            md_urls.extend(await repo_svc.get_md_urls(repo_url.strip()))

        print(f"Found the following md URLs: {md_urls}")
    except Exception as e:
        print(f"Build error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        repo_svc.finalize()

# define `chunker_svc_tester` as a command processor to test repo service.
async def chunker_svc_tester(_: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    chunker_svc = SemanticChunkerService(cfg_svc)

    try:
        sample_text = """
        # Big Tech AI Initiatives
        
        ## Google's AI Strategy
        Google has been investing heavily in artificial intelligence research and development.
        Their main focus areas include:
        
        - Large language models (LaMDA, PaLM, Gemini)
        - Computer vision and image recognition
        - Natural language processing
        - AI-powered search improvements
        
        The company's DeepMind division continues to push the boundaries of AI research,
        with breakthrough achievements in protein folding prediction and game playing.
        
        ## Microsoft's Partnership with OpenAI
        Microsoft's strategic partnership with OpenAI has positioned them as a leader
        in the generative AI space. Key developments include:
        
        1. Integration of GPT models into Office 365
        2. Azure OpenAI Service for enterprise customers
        3. Investment in OpenAI's continued research
        """
        
        chunks = await chunker_svc.chunk_document(
            content=sample_text,
            title="Big Tech AI Report",
            source="example.md"
        )
        
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i}: {len(chunk.content)} chars")
            print(f"Content: {chunk.content[:100]}...")
            print(f"Metadata: {chunk.metadata}")
            print("---")
    except Exception as e:
        print(f"Test error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        chunker_svc.finalize()

# define `graphiti_svc_tester` as a command processor to test repo service.
async def graphiti_svc_tester(_: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    graph_svc = GraphitiGraphService(cfg_svc)

    class Camera(BaseModel):
        """A camera entity with location information."""
        id: str = Field(..., description="Unique identifier for the camera")
        priority: str = Field(..., description="Camera priority")
        location: str = Field(..., description="Camera location")
        campus: str = Field(..., description="Camera campus")

    class Agent(BaseModel):
        """An agent entity with manager information."""
        id: str = Field(..., description="Unique identifier for the agent")
        manager: str = Field(..., description="Agent manager")

    class AgentManager(BaseModel):
        """An agent manager entity."""
        id: str = Field(..., description="Unique identifier for the agent manager")

    class Frame(BaseModel):
        """An frame entity."""
        id: str = Field(..., description="Unique identifier for the frame")
        type: str = Field(..., description="Frame type")
        url: str = Field(..., description="Frame URL")
        frame_date: Optional[datetime] = Field(None, description="Frame date")

    class Alert(BaseModel):
        """An alert relationship."""
        type: str = Field(..., description="alert type")
        confidence_level: float = Field(..., description="alert confidence level")
        alert_date: Optional[datetime] = Field(None, description="Alert date")

    class Invocation(BaseModel):
        """An invocation relationship."""
        invocation_date: Optional[datetime] = Field(None, description="Invocation start date")

    class Pairing(BaseModel):
        """An pairing relationship."""
        invocation_date: Optional[datetime] = Field(None, description="Pairing start date")

    entity_types = {
        "Camera": Camera,
        "Agent": Agent,
        "AgentManager": AgentManager,
        "Frame": Frame
    }
    
    edge_types = {
        "Alert": Alert,
        "Invocation": Invocation,
        "Pairing": Pairing
    }
    edge_type_map = {
        ("Camera", "Frame"): ["Alert"],
        ("Agent", "AgentManager"): ["Invocation"],
        ("Camera", "Agent"): ["Pairing"]
    }
    
    try:
        messages = [
            "High Priority Camera beta_lab_101 located in Building B in San Antonio Campus.",
            "High Priority Camera beta_lab_102 located in Building C in Phoenix Campus.",
            "High Priority Camera beta_lab_103 located in Building D in Charlotte Campus.",
            "Agent Manager AM_9100 starts Agent AA-001 at 2025-06-29T08:00:05 AM CST.",
            "Agent Manager AM_9100 starts Agent AA-002 at 2025-06-29T09:10:05 AM CST.",
            "Agent Manager AM_9100 starts Agent AA-003 at 2025-06-29T09:15:09 AM CST.",
            "Agent AA-001 pairs with Camera beta_lab_101 at 2025-06-29T08:00:09 AM CST.",
            "Agent AA-002 pairs with Camera beta_lab_102 at 2025-06-29T09:10:09 AM CST.",
            "Agent AA-003 pairs with Camera beta_lab_103 at 2025-06-29T09:05:11 AM CST.",
            "Frame https://frames.com/382329 arriving on 2025-06-29T10:00:03 AM CST on camera beta_lab_101 resulted in weapon alert of 7.1 confidence level on 2025-06-29T10:00:05 AM CST.",
            "Agent Manager AM_9100 starts Agent AA-010 at 2025-06-29T11:11:01 AM CST.",
            "Agent AA-010 pairs with Camera beta_lab_101 at 2025-06-29T11:11:11 AM CST."
        ]

        await graph_svc.clear_graph()

        for i, message in enumerate(messages):
            print(f"Processing message: {message}")
            try:
                await graph_svc.add_episode_aux(
                    name="Camera Event Update " + str(i),
                    episode_body=message,
                    source_description="Camera Events",
                    reference_time=datetime.now(),
                    entity_types=entity_types,
                    edge_types=edge_types,
                    edge_type_map=edge_type_map
                )
            except Exception as e:
                print(f"Error processing message '{message}': {e}")
                continue

        # print("Graph has been populated with the following entities and relationships:")
        # graph_stats = await graph_svc.get_graph_statistics()
        # print(f"Graph Statistics: {graph_stats}")

        query = "relationship entities involving beta_lab_101 entity"
        results = await graph_svc.search(
            query=query
        )
        print(f"0. Search results for query '{query}': {len(results)} found.\n{results}")   

        query = "Tell me about cameras"
        search_type = "node"
        results = await graph_svc.search_aux(
            query=query,
            search_type=search_type,
            custom_types=["Camera"]
        )
        print(f"1. Search results for query '{query}' with type '{search_type}': {len(results)} found.\n{results}")   

        query = "Tell me about camera-agent relationships"
        search_type = "edge"
        results = await graph_svc.search_aux(
            query=query,
            search_type=search_type,
            custom_types=["Pairing"]
        )
        print(f"2. Search results for query '{query}' with type '{search_type}': {len(results)} found.\n{results}")   

        query = "Tell me about camera-frame relationships"
        search_type = "edge"
        results = await graph_svc.search_aux(
            query=query,
            search_type=search_type,
            custom_types=["Alert"]
        )
        print(f"3. Search results for query '{query}' with type '{search_type}': {len(results)} found.\n{results}")   

        query = "Tell me about agent-agent manager relationships"
        search_type = "edge"
        results = await graph_svc.search_aux(
            query=query,
            search_type=search_type,
            custom_types=["Invocation"]
        )
        print(f"4. Search results for query '{query}' with type '{search_type}': {len(results)} found.\n{results}")   

    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        await graph_svc.finalize()

# define `neo4j_svc_tester` as a command processor to test repo service.
async def neo4j_svc_tester(_: str) -> None:
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    graph_svc = Neo4jGraphService(cfg_svc)

    try:
        await graph_svc.clear_graph()

        scenarios: Dict[str, Dict[str, Any]] = {
            "cameras": {
                "query": """
                    CREATE (sat:Campus {name: $campussat})
                    CREATE (phx:Campus {name: $campusphx})
                    CREATE (col:Campus {name: $campuscol})
                    CREATE (sata:Building {name: $buildingsata})
                    CREATE (satb:Building {name: $buildingsatb})
                    CREATE (satc:Building {name: $buildingsatc})
                    CREATE (phxa:Building {name: $buildingphxa})
                    CREATE (cola:Building {name: $buildingcola})
                    CREATE (sata)-[:LOCATED_IN]->(sat)
                    CREATE (satb)-[:LOCATED_IN]->(sat)
                    CREATE (satc)-[:LOCATED_IN]->(sat)
                    CREATE (phxa)-[:LOCATED_IN]->(phx)
                    CREATE (cola)-[:LOCATED_IN]->(col)
                    CREATE (cam1:Camera {name: $camera1})
                    CREATE (cam2:Camera {name: $camera2})
                    CREATE (cam3:Camera {name: $camera3})
                    CREATE (cam1)-[:LOCATED_IN]->(sata)
                    CREATE (cam2)-[:LOCATED_IN]->(phxa)
                    CREATE (cam3)-[:LOCATED_IN]->(cola)
                """,
                "params": {
                    "campussat": "San Antonio",
                    "campusphx": "Phenix",
                    "campuscol": "Colorado Springs",
                    "buildingsata": "SAT-A",
                    "buildingsatb": "SAT-B",
                    "buildingsatc": "SAT-C",
                    "buildingphxa": "PHX-A",
                    "buildingcola": "COL-A",
                    "camera1": "beta_lab_101",
                    "camera2": "beta_lab_102",
                    "camera3": "beta_lab_103",
                }
            },
            "agents": {
                "query": """
                    CREATE (mgr1:Manager {name: $manager1})
                    CREATE (agent1:Agent {name: $agent1})
                    CREATE (agent2:Agent {name: $agent2})
                    CREATE (agent3:Agent {name: $agent3})
                    CREATE (mgr1)-[:INVOKED {invoked_at: datetime()}]->(agent1)
                    CREATE (mgr1)-[:INVOKED {invoked_at: datetime()}]->(agent2)
                    CREATE (mgr1)-[:INVOKED {invoked_at: datetime()}]->(agent3)
                    WITH agent1, agent2, agent3
                    MATCH (cam1:Camera {name: $camera1}), (cam2:Camera {name: $camera2}), (cam3:Camera {name: $camera3})
                    CREATE (agent1)-[:PAIRED {paired_at: datetime()}]->(cam1)
                    CREATE (agent2)-[:PAIRED {paired_at: datetime()}]->(cam2)
                    CREATE (agent3)-[:PAIRED {paired_at: datetime()}]->(cam3)
                """,
                "params": {
                    "manager1": "Manager 1",
                    "agent1": "Agent 1",
                    "agent2": "Agent 2",
                    "agent3": "Agent 3",
                    "camera1": "beta_lab_101",
                    "camera2": "beta_lab_102",
                    "camera3": "beta_lab_103"
                }
            },
            "transactions": {
                "query": """
                    MATCH (agent1:Agent {name: $agent1})-[r:PAIRED]->(cam1:Camera {name: $camera1})
                    SET r.severed_at = datetime()
                    """,
                "params": {
                    "agent1": "Agent 1",
                    "camera1": "beta_lab_101",
                }
            },
        }

        for i, (scenario_key, scenario) in enumerate(scenarios.items()):
            query = scenario.get("query", "")
            params = scenario.get("params", {})

            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing scenario '{scenario_key}': {e}")

        # Add-hoc queries of cameras
        cameras = ["beta_lab_101", "beta_lab_104", "beta_lab_105"]

        for camera in cameras:
            query = f"""
                MERGE (c:Camera {{name: $camera}})
                    ON CREATE SET
                        c.priority = $priority, 
                        c.source = $source
                    ON MATCH SET
                        c.priority = $priority, 
                        c.source = $source
                RETURN c
            """

            params = {
                "camera": camera,
                "priority": "High",
                "source": "source_system",
            }
            try:
                _ = await graph_svc.query(
                    query,
                    params
                )
            except Exception as e:
                print(f"Error processing ad-hoc query: {e}")

        # query the database
        query = """
            MATCH (c:Camera {priority: $priority})
            RETURN c.name as camera, c.priority as priority, c.source as source
            ORDER BY c.name DESC
        """
        params = {
            "priority": "High"
        }
        records = await graph_svc.query(query, params)
        print(f"Cameras Query '{query}' returned {len(records)} records:")
        for row in records:
            print(row)

        query = """
            MATCH (m:Manager)-[:INVOKED]->(a:Agent)
            RETURN a.name as agent, m.name as manager
            ORDER BY a.name DESC
        """
        records = await graph_svc.query(query)
        print(f"Agents Query '{query}' returned {len(records)} records:")
        for row in records:
            print(row)

        query = "CALL dbms.components()"
        records = await graph_svc.query(query)
        print(f"Components Query '{query}' returned {len(records)} records:")
        for row in records:
            print(row)
    except Exception as e:
        print(f"Ingest error occurred: {e}")
    finally:
        # Finalize services
        cfg_svc.finalize()
        await graph_svc.finalize()

# define a command processors mapping where each key is a command name
# and the value is an async function that performs the command. 
# the processor is a callable function that takes variant 
# input arguments, returns None and must be awaited. 
processors: Dict[str, Callable[..., Awaitable [None]]] = {
    "test_repo": repo_svc_tester,
    "test_chunker": chunker_svc_tester,
    "test_graphiti": graphiti_svc_tester,
    "test_neo4j": neo4j_svc_tester
}

async def main():
    parser = argparse.ArgumentParser(description="CLI Processor for various commands.")
    parser.add_argument("proc_name", help="processor command")
    parser.add_argument("arg1", help="comma-delimited repo URLs to iterate through looking for .md URLs")
    args = parser.parse_args()

    if not args.proc_name:
        print("No proc name is providd. Please provide a processor i.e. build.")
        sys.exit(1)

    if args.proc_name not in processors:
        print(f"Unknown command: {args.proc_name}. Available commands: {', '.join(processors.keys())}")
        sys.exit(1)

    if not args.arg1:
        print("No arg1 provided. Please provide an arg1.")
        sys.exit(1)

    await processors[args.proc_name](args.arg1)

if __name__ == "__main__":
    asyncio.run(main())  # Pass command-line arguments to main
