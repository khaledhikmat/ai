"""
Security Knowledge Base MCP Server - Delegation Implementation
A Model Context Protocol server for managing security-related data in Neo4j
"""

import json
import logging
from typing import Any, Dict, List
from dataclasses import dataclass

import fastmcp

from service.config.envvars import EnvVarsConfigService
from service.security.typex import ISecurityKnowledgeService
from service.security.neo4j import Neo4jSecurityKnowledgeService
from mcp_servers.typex import MCPServerParameters

logger = logging.getLogger(__name__)


@dataclass
class SecurityMCPDeps:
    """Dependencies for the Security MCP server."""
    security_service: ISecurityKnowledgeService

def initialize_mcp_params() -> MCPServerParameters:
    """Initialize security MCP server parameters"""
    # Initialize services
    config_service = EnvVarsConfigService()
    security_service = Neo4jSecurityKnowledgeService(config_service)
    
    # Initialize Neo4j connection synchronously by calling the sync method directly
    security_service._initialize_sync()
    
    deps = SecurityMCPDeps(security_service=security_service)
    
    # Create FastMCP server
    mcp = fastmcp.FastMCP("Security Knowledge Base")
    
    # Register resources
    @mcp.resource("security://employees")
    def get_employees() -> str:
        """All employees in the security system"""
        nodes = deps.security_service.search_nodes("Employee", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    @mcp.resource("security://officers")  
    def get_officers() -> str:
        """All security officers in the system"""
        nodes = deps.security_service.search_nodes("Officer", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    @mcp.resource("security://visitors")
    def get_visitors() -> str:
        """All visitors in the security system"""
        nodes = deps.security_service.search_nodes("Visitor", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    @mcp.resource("security://vehicles")
    def get_vehicles() -> str:
        """All vehicles in the security system"""
        nodes = deps.security_service.search_nodes("Vehicle", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    @mcp.resource("security://campuses")
    def get_campuses() -> str:
        """All campuses in the security system"""
        nodes = deps.security_service.search_nodes("Campus", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    @mcp.resource("security://incidents")
    def get_incidents() -> str:
        """All security incidents in the system"""
        nodes = deps.security_service.search_nodes("Incident", {}, limit=100)
        return json.dumps(nodes, indent=2, default=str)

    # Register tools
    @mcp.tool()
    async def create_employee(
        name: str, 
        employee_id: str, 
        type: str, 
        department: str,
        campus: str = None,
        work_shift: str = None,
        manager: str = None,
        photo: str = None,
        vehicles: List[str] = None
    ) -> str:
        """Create a new employee record
        
        Args:
            name: Employee name
            employee_id: Unique employee ID
            type: Employee type (Regular or Contractor)  
            department: Department name
            campus: Campus location
            work_shift: Work shift schedule
            manager: Manager name
            photo: Photo URL or path
            vehicles: List of vehicle identifiers
        """
        try:
            # Real-world async operations you might want:
            
            # 1. Validate employee ID doesn't already exist (could be async DB call)
            # 2. Send notification to HR system (async API call)
            # 3. Log audit trail (async logging)
            # 4. Generate employee badge (async file operation)
            
            # For now, just create the employee
            result = deps.security_service.create_employee(
                name=name,
                employee_id=employee_id,
                type=type,
                department=department,
                campus=campus,
                work_shift=work_shift,
                manager=manager,
                photo=photo,
                vehicles=vehicles or []
            )
            
            # Future: Could add async post-processing here
            # await send_hr_notification(employee_id)
            # await audit_log.log_employee_creation(employee_id)
            
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating employee: {str(e)}"

    @mcp.tool()
    def create_officer(
        name: str, 
        employee_id: str, 
        type: str, 
        department: str,
        campus: str = None,
        work_shift: str = None,
        manager: str = None,
        photo: str = None,
        vehicles: List[str] = None
    ) -> str:
        """Create a new security officer record
        
        Args:
            name: Officer name
            employee_id: Unique employee ID
            type: Officer type (Regular or Contractor)
            department: Department name
            campus: Campus location
            work_shift: Work shift schedule
            manager: Manager name
            photo: Photo URL or path
            vehicles: List of vehicle identifiers
        """
        try:
            result = deps.security_service.create_officer(
                name=name,
                employee_id=employee_id,
                type=type,
                department=department,
                campus=campus,
                work_shift=work_shift,
                manager=manager,
                photo=photo,
                vehicles=vehicles or []
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating officer: {str(e)}"

    @mcp.tool()
    def create_visitor(
        name: str,
        age: int = None,
        hair_color: str = None,
        eye_color: str = None,
        skin: str = None,
        gender: str = None,
        photo: str = None,
        restricted: bool = False,
        vehicles: List[str] = None,
        campuses: List[str] = None
    ) -> str:
        """Create a new visitor record
        
        Args:
            name: Visitor name
            age: Visitor age
            hair_color: Hair color
            eye_color: Eye color  
            skin: Skin description
            gender: Gender
            photo: Photo URL or path
            restricted: Whether visitor has restrictions
            vehicles: List of vehicle identifiers
            campuses: List of allowed campuses
        """
        try:
            result = deps.security_service.create_visitor(
                name=name,
                age=age,
                hair_color=hair_color,
                eye_color=eye_color,
                skin=skin,
                gender=gender,
                photo=photo,
                restricted=restricted,
                vehicles=vehicles or [],
                campuses=campuses or []
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating visitor: {str(e)}"

    @mcp.tool()
    def create_vehicle(
        make: str,
        model: str, 
        license: str,
        name: str = None,
        year: int = None,
        color: str = None,
        decal: str = None
    ) -> str:
        """Create a new vehicle record
        
        Args:
            make: Vehicle make
            model: Vehicle model
            license: License plate number
            name: Vehicle name/identifier
            year: Vehicle year
            color: Vehicle color
            decal: Decal information
        """
        try:
            result = deps.security_service.create_vehicle(
                name=name,
                make=make,
                model=model,
                year=year,
                license=license,
                color=color,
                decal=decal
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating vehicle: {str(e)}"

    @mcp.tool()
    def create_campus(
        name: str,
        address: str,
        city: str,
        state: str
    ) -> str:
        """Create a new campus record
        
        Args:
            name: Campus name
            address: Campus address
            city: City
            state: State
        """
        try:
            result = deps.security_service.create_campus(
                name=name,
                address=address,
                city=city,
                state=state
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating campus: {str(e)}"

    @mcp.tool()
    def create_incident(
        number: str,
        campus: str,
        start_datetime: str,
        narration: str,
        end_datetime: str = None,
        assigned_officer: str = None,
        involved_vehicles: List[str] = None,
        involved_employees: List[str] = None,
        involved_visitors: List[str] = None
    ) -> str:
        """Create a new security incident record
        
        Args:
            number: Incident number
            campus: Campus where incident occurred
            start_datetime: Incident start datetime (ISO format)
            narration: Incident description
            end_datetime: Incident end datetime (ISO format)
            assigned_officer: Officer assigned to incident
            involved_vehicles: List of involved vehicles
            involved_employees: List of involved employees
            involved_visitors: List of involved visitors
        """
        try:
            result = deps.security_service.create_incident(
                number=number,
                campus=campus,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                narration=narration,
                assigned_officer=assigned_officer,
                involved_vehicles=involved_vehicles or [],
                involved_employees=involved_employees or [],
                involved_visitors=involved_visitors or []
            )
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error creating incident: {str(e)}"

    @mcp.tool()
    async def search_nodes(
        node_type: str,
        filters: Dict[str, Any] = None,
        limit: int = 50
    ) -> str:
        """Search for nodes by type with filters
        
        Args:
            node_type: Type of node (Employee, Officer, Visitor, Vehicle, Campus, Incident)
            filters: Dictionary of property filters
            limit: Maximum number of results (max 100)
        """
        try:
            valid_types = ["Employee", "Officer", "Visitor", "Vehicle", "Campus", "Incident"]
            if node_type not in valid_types:
                return f"Invalid node_type. Must be one of: {valid_types}"
            
            limit = min(limit, 100)  # Cap at 100
            
            # This is async because search could be expensive and we might want to:
            # 1. Add caching layer (async cache lookup)
            # 2. Log search queries for analytics (async logging)
            # 3. Rate limiting (async check)
            # 4. Permission checking (async auth service call)
            
            result = deps.security_service.search_nodes(node_type, filters or {}, limit)
            
            # Future async operations:
            # await analytics_service.log_search(node_type, filters)
            # await cache_service.store_search_result(cache_key, result)
            
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error searching nodes: {str(e)}"

    @mcp.tool()
    def create_relationship(
        from_type: str,
        from_id: str,
        relationship_type: str,
        to_type: str,
        to_id: str,
        properties: Dict[str, Any] = None
    ) -> str:
        """Create relationships between nodes
        
        Args:
            from_type: Source node type
            from_id: Source node identifier
            relationship_type: Type of relationship
            to_type: Target node type  
            to_id: Target node identifier
            properties: Additional relationship properties
        """
        try:
            valid_types = ["Employee", "Officer", "Visitor", "Vehicle", "Campus", "Incident"]
            valid_rel_types = ["MANAGES", "WORKS_IN", "OWNS", "INVOLVES", "ASSIGNS", "HAPPENED_IN"]
            
            if from_type not in valid_types or to_type not in valid_types:
                return f"Invalid node types. Must be one of: {valid_types}"
            
            if relationship_type not in valid_rel_types:
                return f"Invalid relationship type. Must be one of: {valid_rel_types}"
            
            result = deps.security_service.create_relationship(
                from_type, from_id, relationship_type, 
                to_type, to_id, properties or {}
            )
            return f"Relationship created: {result}"
        except Exception as e:
            return f"Error creating relationship: {str(e)}"

    @mcp.tool()
    def get_relationships(node_type: str, node_id: str) -> str:
        """Get all relationships for a specific node
        
        Args:
            node_type: Type of node
            node_id: Node identifier
        """
        try:
            valid_types = ["Employee", "Officer", "Visitor", "Vehicle", "Campus", "Incident"]
            if node_type not in valid_types:
                return f"Invalid node_type. Must be one of: {valid_types}"
            
            result = deps.security_service.get_relationships(node_type, node_id)
            return json.dumps(result, default=str)
        except Exception as e:
            return f"Error getting relationships: {str(e)}"
    
    return MCPServerParameters(
        name="Security Knowledge Base",
        description="MCP server for managing security-related data in Neo4j",
        deps=deps,
        server=mcp
    )


def finalize_mcp_params(params: MCPServerParameters) -> None:
    """Clean up security MCP server resources"""
    if params.deps and params.deps.security_service:
        params.deps.security_service._finalize_sync()
    logger.info("Security MCP server cleanup completed")