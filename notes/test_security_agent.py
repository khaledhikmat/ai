#!/usr/bin/env python3
"""
Test script for the Security Agent
"""

import asyncio
import os
from dotenv import load_dotenv

from notes.agent_mcp_client import initialize_agent_params, finalize_agent_params

load_dotenv()

async def test_security_agent():
    """Test the security agent functionality."""
    
    print("🛡️  Testing Security Agent")
    print("=" * 50)
    
    try:
        # Initialize agent
        print("🔧 Initializing Security Agent...")
        agent_params = await initialize_agent_params()
        
        print(f"✅ {agent_params.title}")
        print(f"📋 {agent_params.description}")
        print()
        
        # Test queries
        test_queries = [
            "List all available tools from the MCP server",
            "Create a new employee named John Doe with ID EMP001",
            "Search for employees in the security database",
            "Create a security incident report for a break-in at the main entrance"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 60)
            
            try:
                result = await agent_params.agent.run(
                    query,
                    deps=agent_params.deps
                )
                
                print(f"🤖 Agent Response:")
                print(result.data)
                
            except Exception as e:
                print(f"❌ Error in test {i}: {e}")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        
    finally:
        # Clean up
        if 'agent_params' in locals():
            print("\n🧹 Cleaning up...")
            await finalize_agent_params(agent_params)
            print("✅ Cleanup complete")


if __name__ == "__main__":
    # Set MCP server URL for testing
    if "MCP_SERVER_URL" not in os.environ:
        os.environ["MCP_SERVER_URL"] = "http://localhost:8000"
        print(f"🔗 Using default MCP server URL: {os.environ['MCP_SERVER_URL']}")
    else:
        print(f"🔗 Using MCP server URL: {os.environ['MCP_SERVER_URL']}")
    
    asyncio.run(test_security_agent())