import logging
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase

from service.config.typex import IConfigService

logger = logging.getLogger(__name__)


class Neo4jSecurityKnowledgeService:
    """Neo4j implementation of Security Knowledge service"""
    
    def __init__(self, config_service: IConfigService):
        self.config_service = config_service
        self.driver = None
        
    async def initialize(self) -> None:
        """Initialize the Neo4j connection (async version)"""
        self._initialize_sync()
        
    def _initialize_sync(self) -> None:
        """Initialize the Neo4j connection (sync version)"""
        neo4j_uri = self.config_service.get_neo4j_uri()
        neo4j_username = self.config_service.get_neo4j_user()
        neo4j_password = self.config_service.get_neo4j_password()
        
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        self.create_constraints_and_indexes()
        logger.info("Connected to Neo4j database for Security Knowledge Base")
        
    async def finalize(self) -> None:
        """Clean up Neo4j driver (async version)"""
        self._finalize_sync()
        
    def _finalize_sync(self) -> None:
        """Clean up Neo4j driver (sync version)"""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
    
    def create_constraints_and_indexes(self) -> None:
        """Create necessary constraints and indexes for the security schema"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            constraints_and_indexes = [
                # Unique constraints
                "CREATE CONSTRAINT employee_id IF NOT EXISTS FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE",
                "CREATE CONSTRAINT officer_id IF NOT EXISTS FOR (o:Officer) REQUIRE o.employee_id IS UNIQUE", 
                "CREATE CONSTRAINT incident_number IF NOT EXISTS FOR (i:Incident) REQUIRE i.number IS UNIQUE",
                "CREATE CONSTRAINT vehicle_license IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.license IS UNIQUE",
                "CREATE CONSTRAINT campus_name IF NOT EXISTS FOR (c:Campus) REQUIRE c.name IS UNIQUE",
                
                # Indexes for performance
                "CREATE INDEX employee_name IF NOT EXISTS FOR (e:Employee) ON (e.name)",
                "CREATE INDEX officer_name IF NOT EXISTS FOR (o:Officer) ON (o.name)",
                "CREATE INDEX visitor_name IF NOT EXISTS FOR (v:Visitor) ON (v.name)",
                "CREATE INDEX incident_datetime IF NOT EXISTS FOR (i:Incident) ON (i.start_datetime)",
                "CREATE INDEX campus_city IF NOT EXISTS FOR (c:Campus) ON (c.city)"
            ]
            
            for constraint in constraints_and_indexes:
                try:
                    session.run(constraint)
                    logger.info(f"Applied: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint/Index might already exist: {e}")
    
    def create_employee(self, **properties) -> Dict[str, Any]:
        """Create an Employee node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (e:Employee {
                    name: $name,
                    employee_id: $employee_id,
                    type: $type,
                    department: $department,
                    campus: $campus,
                    work_shift: $work_shift,
                    manager: $manager,
                    photo: $photo,
                    vehicles: $vehicles,
                    created_at: datetime()
                })
                RETURN e
                """,
                **properties
            )
            return dict(result.single()["e"])
    
    def create_officer(self, **properties) -> Dict[str, Any]:
        """Create an Officer node (inherits Employee properties)"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (o:Officer {
                    name: $name,
                    employee_id: $employee_id,
                    type: $type,
                    department: $department,
                    campus: $campus,
                    work_shift: $work_shift,
                    manager: $manager,
                    photo: $photo,
                    vehicles: $vehicles,
                    created_at: datetime()
                })
                RETURN o
                """,
                **properties
            )
            return dict(result.single()["o"])
    
    def create_visitor(self, **properties) -> Dict[str, Any]:
        """Create a Visitor node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (v:Visitor {
                    name: $name,
                    age: $age,
                    hair_color: $hair_color,
                    eye_color: $eye_color,
                    skin: $skin,
                    gender: $gender,
                    photo: $photo,
                    restricted: $restricted,
                    vehicles: $vehicles,
                    campuses: $campuses,
                    created_at: datetime()
                })
                RETURN v
                """,
                **properties
            )
            return dict(result.single()["v"])
    
    def create_vehicle(self, **properties) -> Dict[str, Any]:
        """Create a Vehicle node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (v:Vehicle {
                    name: $name,
                    make: $make,
                    model: $model,
                    year: $year,
                    license: $license,
                    color: $color,
                    decal: $decal,
                    created_at: datetime()
                })
                RETURN v
                """,
                **properties
            )
            return dict(result.single()["v"])
    
    def create_campus(self, **properties) -> Dict[str, Any]:
        """Create a Campus node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (c:Campus {
                    name: $name,
                    address: $address,
                    city: $city,
                    state: $state,
                    created_at: datetime()
                })
                RETURN c
                """,
                **properties
            )
            return dict(result.single()["c"])
    
    def create_incident(self, **properties) -> Dict[str, Any]:
        """Create an Incident node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (i:Incident {
                    number: $number,
                    campus: $campus,
                    start_datetime: datetime($start_datetime),
                    end_datetime: datetime($end_datetime),
                    narration: $narration,
                    assigned_officer: $assigned_officer,
                    involved_vehicles: $involved_vehicles,
                    involved_employees: $involved_employees,
                    involved_visitors: $involved_visitors,
                    created_at: datetime()
                })
                RETURN i
                """,
                **properties
            )
            return dict(result.single()["i"])
    
    def create_relationship(self, from_type: str, from_id: str, rel_type: str, 
                          to_type: str, to_id: str, properties: Dict = None) -> bool:
        """Create relationships between nodes"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            if properties is None:
                properties = {}
                
            query = f"""
            MATCH (from:{from_type}), (to:{to_type})
            WHERE from.employee_id = $from_id OR from.name = $from_id OR from.number = $from_id OR from.license = $from_id
            AND to.employee_id = $to_id OR to.name = $to_id OR to.number = $to_id OR to.license = $to_id
            CREATE (from)-[r:{rel_type}]->(to)
            SET r += $properties
            RETURN r
            """
            
            result = session.run(query, from_id=from_id, to_id=to_id, properties=properties)
            return result.single() is not None
    
    def search_nodes(self, node_type: str, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """Search nodes by type with optional filters"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            where_clause = ""
            params = {"limit": limit}
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        conditions.append(f"n.{key} CONTAINS $filter_{key}")
                        params[f"filter_{key}"] = value
                    else:
                        conditions.append(f"n.{key} = $filter_{key}")
                        params[f"filter_{key}"] = value
                
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
            
            query = f"""
            MATCH (n:{node_type})
            {where_clause}
            RETURN n
            LIMIT $limit
            """
            
            result = session.run(query, **params)
            return [dict(record["n"]) for record in result]
    
    def get_relationships(self, node_type: str, node_id: str) -> List[Dict]:
        """Get all relationships for a specific node"""
        if not self.driver:
            raise RuntimeError("Service not initialized. Call initialize() first.")
            
        with self.driver.session() as session:
            query = f"""
            MATCH (n:{node_type})-[r]-(m)
            WHERE n.employee_id = $node_id OR n.name = $node_id OR n.number = $node_id OR n.license = $node_id
            RETURN type(r) as relationship_type, m, labels(m) as node_types
            """
            
            result = session.run(query, node_id=node_id)
            return [
                {
                    "relationship_type": record["relationship_type"],
                    "connected_node": dict(record["m"]),
                    "connected_node_types": record["node_types"]
                }
                for record in result
            ]