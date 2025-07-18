from typing import List, Dict, Any, Optional, Protocol
from pydantic import BaseModel
from datetime import datetime

from graphiti_core.nodes import EpisodeType        

# graph services must implement this protocol
class IGraphService(Protocol): 
    def expose_driver(self) -> Any:
        """Expose the driver for the graph service."""
        pass

    async def add_episode(
        self,
        episode_id: str,
        content: str,
        source: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an episode to the knowledge graph."""
        pass

    async def add_episode_aux(
        self,
        name: str,
        episode_body: str,
        source_description: str,
        reference_time: datetime,
        source: EpisodeType = EpisodeType.message,
        group_id: str | None = None,
        uuid: str | None = None,
        update_communities: bool = False,
        entity_types: dict[str, BaseModel] | None = None,
        excluded_entity_types: list[str] | None = None,
        previous_episode_uuids: list[str] | None = None,
        edge_types: dict[str, BaseModel] | None = None,
        edge_type_map: dict[tuple[str, str], list[str]] | None = None,
    ) -> None:
        """Add an aux episode to the knowledge graph."""
        pass

    async def query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Any], List[str]]:
        """
        Query the knowledge graph.
        """
        pass

    async def search(
        self,
        query: str,
        excluded_entity_types: list[str] | None = None,
        use_hybrid_search: bool = True
    ) -> List[Dict[str, Any]]:
        """Search the knowledge graph."""
        pass

    async def search_aux(
        self,
        query: str,
        search_type: str,
        custom_types: list[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Search the knowledge graph using custom types."""
        pass

    async def get_related_entities(
        self,
        entity_name: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> Dict[str, Any]:
        """Get entities related to a given entity."""
        pass

    async def get_entity_timeline(
        self,
        entity_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get timeline of facts for an entity."""
        pass

    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        pass

    async def clear_graph(self) -> None:
        """Clear the knowledge graph."""
        pass

    async def close(self) -> None:
        """Close the graph service connection."""
        pass

    async def finalize(self) -> None:
        """Destruct the service and close resources."""
        pass

