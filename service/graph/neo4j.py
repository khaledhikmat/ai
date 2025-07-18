from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from neo4j import GraphDatabase

from service.config.typex import IConfigService

# compliant with IGraphService protocol
# please note that Neo4j Python driver is synchronous
# so we use asyncio to run it in a thread executor
# this is a simple implementation that does not use any advanced features of Neo4j
# such as transactions, batching, or advanced querying capabilities
# it is meant to be a starting point for a more complex implementation
# also this service provides a determintistc implementation where nodes
# and relationships are created based on the Cypher query provided
class Neo4jGraphService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        uri = self.config_service.get_neo4j_uri()
        user = self.config_service.get_neo4j_user()
        password = self.config_service.get_neo4j_password()
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def expose_driver(self) -> Any:
        """Expose the driver for the graph service."""
        return self.driver

    async def add_episode(
        self,
        episode_id: str,
        content: str,
        source: str,
        timestamp: Optional[datetime] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an episode to the knowledge graph.
        Assume that the content is the Cypher query
        Ignore everything else
        """
        return None

    async def add_episode_aux(
        self,
        name: str,
        episode_body: str,
        source_description: str,
        reference_time: datetime,
        source: Any = None,
        group_id: str | None = None,
        uuid: str | None = None,
        update_communities: bool = False,
        entity_types: dict[str, BaseModel] | None = None,
        excluded_entity_types: list[str] | None = None,
        previous_episode_uuids: list[str] | None = None,
        edge_types: dict[str, BaseModel] | None = None,
        edge_type_map: dict[tuple[str, str], list[str]] | None = None,
    ) -> None:
        """
        Not implemented in this service.
        Add an aux episode to the knowledge graph."""
        return None

    async def query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Any], List[str]]:
        """
        Query the knowledge graph.
        This is used for writing or reading data
        """
        import asyncio
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.driver.execute_query(query, parameters)
        )

        # return result.records, result.keys  

        records = []
        for record in result.records:
            # Convert Neo4j Record to a dictionary
            record_dict = {key: record.data()[key] for key in record.data()}
            records.append(record_dict)

        return records

    async def search(
        self,
        query: str,
        excluded_entity_types: list[str] | None = None,
        use_hybrid_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Not implemented in this service.
        Search the knowledge graph.
        """
        return []

    async def search_aux(
        self,
        query: str,
        search_type: str,
        custom_types: list[str] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Not implemented in this service.
        Search the knowledge graph using custom types."""
        return []

    async def get_related_entities(
        self,
        entity_name: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Not implemented in this service.
        Get entities related to a given entity.
        """
        return {}

    async def get_entity_timeline(
        self,
        entity_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Not implemented in this service.
        Get timeline of facts for an entity.
        """
        return []

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Not implemented in this service.
        Get statistics about the knowledge graph.
        """
        return {}

    async def clear_graph(self) -> None:
        """
        Not implemented in this service.
        Clear the knowledge graph.
        """
        query = "MATCH (n) DETACH DELETE n"
        # Neo4j Python driver is synchronous, so run in a thread executor for async
        import asyncio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self.driver.execute_query(query)
        )

    async def close(self):
        import asyncio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self.driver.close()
        )

    async def finalize(self) -> None:
        """Destruct the service and close resources."""
        await self.close()

