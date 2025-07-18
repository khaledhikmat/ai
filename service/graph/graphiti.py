from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType        
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.search.search_filters import SearchFilters

from service.config.typex import IConfigService

# compliant with IGraphService protocol
class GraphitiGraphService:
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        self.graphiti = None

    def expose_driver(self) -> Any:
        """Expose the driver for the graph service."""
        return self.graphiti

    async def add_episode(
        self,
        episode_id: str,
        content: str,
        source: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add an episode to the knowledge graph.
        
        Args:
            episode_id: Unique episode identifier
            content: Episode content
            source: Source of the content
            timestamp: Episode timestamp
            metadata: Additional metadata
        """
        await self._initialize()
        
        episode_timestamp = timestamp or datetime.now(timezone.utc)
        
        await self.graphiti.add_episode(
            name=episode_id,
            episode_body=content,
            source=EpisodeType.text,  # Always use text type for our content
            source_description=source,
            reference_time=episode_timestamp
        )
        
        print(f"Added episode {episode_id} to knowledge graph")
    
    async def add_episode_aux(
        self,
        name: str,
        episode_body: str,
        source_description: str,
        reference_time: datetime,
        source: EpisodeType = EpisodeType.text, # Always use text type for our content
        group_id: str = '',
        uuid: str | None = None,
        update_communities: bool = False,
        entity_types: dict[str, BaseModel] | None = None,
        excluded_entity_types: list[str] | None = None,
        previous_episode_uuids: list[str] | None = None,
        edge_types: dict[str, BaseModel] | None = None,
        edge_type_map: dict[tuple[str, str], list[str]] | None = None,
    ) -> None:
        await self._initialize()
        
        await self.graphiti.add_episode(
            name=name,
            episode_body=episode_body,
            source_description=source_description,
            reference_time=reference_time,
            source=source,
            group_id=group_id,
            uuid=uuid,
            update_communities=update_communities,
            entity_types=entity_types,
            excluded_entity_types=excluded_entity_types,
            previous_episode_uuids=previous_episode_uuids,
            edge_types=edge_types,
            edge_type_map=edge_type_map
        )
        print(f"Added episode {name} to knowledge graph")

    async def query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Any], List[str]]:
        """
        Not implemented in this service.
        Search the knowledge graph.
        """
        return []

    async def search(
        self,
        query: str,
        center_node_distance: int = 2,
        use_hybrid_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph.
        
        Args:
            query: Search query
            center_node_distance: Distance from center nodes
            use_hybrid_search: Whether to use hybrid search
        
        Returns:
            Search results
        """
        await self._initialize()
        
        try:
            # Use Graphiti's search method (simplified parameters)
            results = await self.graphiti.search(query)
            
            # Convert results to dictionaries
            return [
                {
                    "fact": result.fact,
                    "uuid": str(result.uuid),
                    "valid_at": str(result.valid_at) if hasattr(result, 'valid_at') and result.valid_at else None,
                    "invalid_at": str(result.invalid_at) if hasattr(result, 'invalid_at') and result.invalid_at else None,
                    "source_node_uuid": str(result.source_node_uuid) if hasattr(result, 'source_node_uuid') and result.source_node_uuid else None
                }
                for result in results
            ]
            
        except Exception as e:
            print(f"Graph search failed: {e}")
            return []
    
    async def search_aux(
        self,
        query: str,
        search_type: str,
        custom_types: list[str] | None = None
    ) -> List[Dict[str, Any]]:
        """Search the knowledge graph using custom types."""
        await self._initialize()
        
        try:
            search_filter = SearchFilters(
                node_labels=custom_types
            )

            if search_type == "edge":
                search_filter = SearchFilters(
                    edge_types=custom_types
                )

            # Use Graphiti's custom search method
            results = await self.graphiti.search_(query, search_filter=search_filter)
            print(f"Search results for query '{query}' with type '{search_type}': {len(results)} found.\n{results}")   
            
            # Convert results to dictionaries
            return [
                {
                    "fact": result.fact,
                    "uuid": str(result.uuid),
                    "valid_at": str(result.valid_at) if hasattr(result, 'valid_at') and result.valid_at else None,
                    "invalid_at": str(result.invalid_at) if hasattr(result, 'invalid_at') and result.invalid_at else None,
                    "source_node_uuid": str(result.source_node_uuid) if hasattr(result, 'source_node_uuid') and result.source_node_uuid else None
                }
                for result in results
            ]
            
        except Exception as e:
            print(f"Graph search failed: {e}")
            return []

    async def get_related_entities(
        self,
        entity_name: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Get entities related to a given entity using Graphiti search.
        
        Args:
            entity_name: Name of the entity
            relationship_types: Types of relationships to follow (not used with Graphiti)
            depth: Maximum depth to traverse (not used with Graphiti)
        
        Returns:
            Related entities and relationships
        """
        await self._initialize()
        
        # Use Graphiti search to find related information about the entity
        results = await self.graphiti.search(f"relationships involving {entity_name}")
        
        # Extract entity information from the search results
        related_entities = set()
        facts = []
        
        for result in results:
            facts.append({
                "fact": result.fact,
                "uuid": str(result.uuid),
                "valid_at": str(result.valid_at) if hasattr(result, 'valid_at') and result.valid_at else None
            })
            
            # Simple entity extraction from fact text (could be enhanced)
            if entity_name.lower() in result.fact.lower():
                related_entities.add(entity_name)
        
        return {
            "central_entity": entity_name,
            "related_facts": facts,
            "search_method": "graphiti_semantic_search"
        }
    
    async def get_entity_timeline(
        self,
        entity_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of facts for an entity using Graphiti.
        
        Args:
            entity_name: Name of the entity
            start_date: Start of time range (not currently used)
            end_date: End of time range (not currently used)
        
        Returns:
            Timeline of facts
        """
        await self._initialize()
        
        # Search for temporal information about the entity
        results = await self.graphiti.search(f"timeline history of {entity_name}")
        
        timeline = []
        for result in results:
            timeline.append({
                "fact": result.fact,
                "uuid": str(result.uuid),
                "valid_at": str(result.valid_at) if hasattr(result, 'valid_at') and result.valid_at else None,
                "invalid_at": str(result.invalid_at) if hasattr(result, 'invalid_at') and result.invalid_at else None
            })
        
        # Sort by valid_at if available
        timeline.sort(key=lambda x: x.get('valid_at') or '', reverse=True)
        
        return timeline
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the knowledge graph.
        
        Returns:
            Graph statistics
        """
        await self._initialize()
        
        # For now, return a simple search to verify the graph is working
        # More detailed statistics would require direct Neo4j access
        try:
            test_results = await self.graphiti.search("test")
            return {
                "graphiti_initialized": True,
                "sample_search_results": len(test_results),
                "note": "Detailed statistics require direct Neo4j access"
            }
        except Exception as e:
            return {
                "graphiti_initialized": False,
                "error": str(e)
            }
    
    async def clear_graph(self):
        """Clear all data from the graph (USE WITH CAUTION)."""
        await self._initialize()
        
        try:
            # Use Graphiti's proper clear_data function with the driver
            await clear_data(self.graphiti.driver)
            print("Cleared all data from knowledge graph")
        except Exception as e:
            print(f"Failed to clear graph using clear_data: {e}")
            # Fallback: Close and reinitialize (this will create fresh indices)
            await self.close()

            # force re-initialization 
            self.graphiti = None
            
            # re-initialize the Graphiti client with fresh indices
            await self._initialize()
            print("Reinitialized Graphiti client (fresh indices created)")

    async def close(self):
        """Close Graphiti connection."""
        if self.graphiti:
            await self.graphiti.close()
            self.graphiti = None
            print("Graphiti client closed")
    
    async def finalize(self) -> None:
        """Destruct the service and close resources."""
        await self.close()

    async def _initialize(self):
        """Initialize Graphiti client lazingly."""
        if self.graphiti:
            return
        
        print("Initializing Graphiti client...")

        try:
            # Create LLMConfig
            llm_config = LLMConfig(
                api_key=self.config_service.get_llm_api_key(),
                model=self.config_service.get_llm_choice(),
                small_model=self.config_service.get_llm_choice(),   
                base_url=self.config_service.get_llm_base_url()
            )
            
            # Create OpenAI LLM client
            llm_client = OpenAIClient(config=llm_config)
            
            # Create OpenAI embedder
            embedder = OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    api_key=self.config_service.get_embedded_api_key(),
                    embedding_model=self.config_service.get_embedded_model(),
                    embedding_dim=self.config_service.get_embedded_dimensions(),
                    base_url=self.config_service.get_embedded_base_url(),
                )
            )
            
            # Initialize Graphiti with custom clients
            self.graphiti = Graphiti(
                self.config_service.get_neo4j_uri(),
                self.config_service.get_neo4j_user(),
                self.config_service.get_neo4j_password(),
                llm_client=llm_client,
                embedder=embedder,
                cross_encoder=OpenAIRerankerClient(
                    client=llm_client, 
                    config=llm_config)
            )
            
            # Build indices and constraints
            await self.graphiti.build_indices_and_constraints()
            
            print(f"Graphiti client initialized successfully with LLM: {self.config_service.get_llm_choice()} and embedder: {self.config_service.get_embedded_model()}")

        except Exception as e:
            print(f"Failed to initialize Graphiti: {e}")
            raise
    
