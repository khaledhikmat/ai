from typing import Any, Dict, List, Protocol


class ISecurityKnowledgeService(Protocol):
    """Interface for Security Knowledge service operations"""
    
    async def initialize(self) -> None:
        """Initialize the security knowledge service"""
        pass
    
    async def finalize(self) -> None:
        """Clean up resources"""
        pass
    
    def create_constraints_and_indexes(self) -> None:
        """Create necessary constraints and indexes for the security schema"""
        pass
    
    # Node creation methods
    def create_employee(self, **properties) -> Dict[str, Any]:
        """Create an Employee node"""
        pass
    
    def create_officer(self, **properties) -> Dict[str, Any]:
        """Create an Officer node (inherits Employee properties)"""
        pass
    
    def create_visitor(self, **properties) -> Dict[str, Any]:
        """Create a Visitor node"""
        pass
    
    def create_vehicle(self, **properties) -> Dict[str, Any]:
        """Create a Vehicle node"""
        pass
    
    def create_campus(self, **properties) -> Dict[str, Any]:
        """Create a Campus node"""
        pass
    
    def create_incident(self, **properties) -> Dict[str, Any]:
        """Create an Incident node"""
        pass
    
    # Relationship methods
    def create_relationship(self, from_type: str, from_id: str, rel_type: str, 
                          to_type: str, to_id: str, properties: Dict = None) -> bool:
        """Create relationships between nodes"""
        pass
    
    # Query methods
    def search_nodes(self, node_type: str, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """Search nodes by type with optional filters"""
        pass
    
    def get_relationships(self, node_type: str, node_id: str) -> List[Dict]:
        """Get all relationships for a specific node"""
        pass