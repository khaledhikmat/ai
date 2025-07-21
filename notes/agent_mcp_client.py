from dataclasses import dataclass
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

from helpers.providers import get_llm_model
from service.config.envvars import EnvVarsConfigService

from agent.typex import AgentParameters
from ..agent.incidents.prompts import SYSTEM_PROMPT


@dataclass
class SecurityAgentDeps:
    """Dependencies for the Security agent."""
    mcp_client: 'MCPHttpClient'


class MCPHttpClient:
    """HTTP client for connecting to MCP server."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id = None
        
    async def initialize(self):
        """Initialize MCP session."""
        try:
            # Initialize MCP session
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "security-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Connected to MCP server: {result}")
                return True
            else:
                print(f"❌ Failed to connect to MCP server: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ MCP connection error: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on the MCP server."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {})
            else:
                print(f"❌ Tool call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return None
    
    async def list_tools(self) -> Optional[Dict[str, Any]]:
        """List available tools from MCP server."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", {})
            else:
                print(f"❌ Failed to list tools: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ List tools error: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global variable to hold the agent instance
security_agent = Agent(
    get_llm_model(),  # get the LLM model based on environment variables
    deps_type=SecurityAgentDeps,
    system_prompt=SYSTEM_PROMPT
)


async def initialize_agent_params() -> AgentParameters:
    """Get the agent parameters."""
    await asyncio.sleep(0.1)
    
    # Initialize services
    cfg_svc = EnvVarsConfigService()
    
    # Get MCP server URL from environment or use localhost
    mcp_url = cfg_svc.get("MCP_SERVER_URL", "http://localhost:8000")
    
    # Initialize MCP client
    mcp_client = MCPHttpClient(mcp_url)
    
    # Try to connect
    connected = await mcp_client.initialize()
    if not connected:
        print(f"⚠️  Warning: Could not connect to MCP server at {mcp_url}")
    
    deps = SecurityAgentDeps(mcp_client=mcp_client)
    
    return AgentParameters(
        title="Security Intelligence Agent",
        description="An agent that manages security incidents, personnel, and operations using MCP server.",
        deps=deps,
        agent=security_agent
    )


async def finalize_agent_params(parameters: AgentParameters) -> None:
    """Finalize the agent dependencies."""
    await parameters.deps.mcp_client.close()


@security_agent.tool
async def create_employee(
    context: RunContext[SecurityAgentDeps], 
    name: str, 
    employee_id: str,
    department: Optional[str] = None,
    position: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> str:
    """Create a new employee record in the security system.
    
    Args:
        context: The run context containing dependencies.
        name: Full name of the employee.
        employee_id: Unique employee identifier.
        department: Employee's department.
        position: Employee's job position.
        email: Employee's email address.
        phone: Employee's phone number.
        
    Returns:
        Result of the employee creation operation.
    """
    arguments = {
        "name": name,
        "employee_id": employee_id
    }
    
    if department:
        arguments["department"] = department
    if position:
        arguments["position"] = position
    if email:
        arguments["email"] = email
    if phone:
        arguments["phone"] = phone
    
    result = await context.deps.mcp_client.call_tool("create_employee", arguments)
    
    if result:
        return f"✅ Employee created successfully: {result}"
    else:
        return "❌ Failed to create employee"


@security_agent.tool
async def search_employees(
    context: RunContext[SecurityAgentDeps], 
    name: Optional[str] = None,
    employee_id: Optional[str] = None,
    department: Optional[str] = None
) -> str:
    """Search for employees in the security system.
    
    Args:
        context: The run context containing dependencies.
        name: Employee name to search for.
        employee_id: Employee ID to search for.
        department: Department to search in.
        
    Returns:
        Search results for employees.
    """
    arguments = {}
    
    if name:
        arguments["name"] = name
    if employee_id:
        arguments["employee_id"] = employee_id
    if department:
        arguments["department"] = department
    
    result = await context.deps.mcp_client.call_tool("search_employees", arguments)
    
    if result:
        return f"🔍 Employee search results: {json.dumps(result, indent=2)}"
    else:
        return "❌ Failed to search employees"


@security_agent.tool
async def create_incident(
    context: RunContext[SecurityAgentDeps],
    incident_type: str,
    description: str,
    location: str,
    reporter_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """Create a new security incident record.
    
    Args:
        context: The run context containing dependencies.
        incident_type: Type of security incident.
        description: Detailed description of the incident.
        location: Location where incident occurred.
        reporter_id: ID of person reporting the incident.
        severity: Severity level of the incident.
        status: Current status of the incident.
        
    Returns:
        Result of the incident creation operation.
    """
    arguments = {
        "incident_type": incident_type,
        "description": description,
        "location": location
    }
    
    if reporter_id:
        arguments["reporter_id"] = reporter_id
    if severity:
        arguments["severity"] = severity
    if status:
        arguments["status"] = status
    
    result = await context.deps.mcp_client.call_tool("create_incident", arguments)
    
    if result:
        return f"🚨 Incident created successfully: {result}"
    else:
        return "❌ Failed to create incident"


@security_agent.tool
async def list_available_tools(context: RunContext[SecurityAgentDeps]) -> str:
    """List all available tools on the MCP server.
    
    Args:
        context: The run context containing dependencies.
        
    Returns:
        List of available MCP server tools.
    """
    result = await context.deps.mcp_client.list_tools()
    
    if result:
        tools = result.get("tools", [])
        tool_list = []
        for tool in tools:
            name = tool.get("name", "unknown")
            description = tool.get("description", "No description")
            tool_list.append(f"• {name}: {description}")
        
        return f"🔧 Available MCP Tools:\n" + "\n".join(tool_list)
    else:
        return "❌ Failed to list tools"