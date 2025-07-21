#!/usr/bin/env python3
"""
MCP Server Runner - Delegation Implementation
Central runner for all MCP servers following the project's delegation pattern
"""

import os
import sys
import logging
from dotenv import load_dotenv

from mcp_servers.typex import MCPServerParameters, MCP_INIT_FNS, MCP_FIN_FNS
from mcp_servers.incidents.server import initialize_mcp_params as init_inc_mcp, finalize_mcp_params as fin_inc_mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-runner")

load_dotenv()

# MCP server initializers and finalizers registry
mcp_init_fns: MCP_INIT_FNS = {
    "inc": init_inc_mcp,
    # Add more MCP servers here as they are implemented
}

mcp_fin_fns: MCP_FIN_FNS = {
    "inc": fin_inc_mcp,
    # Add more MCP servers here as they are implemented
}


def main(mcp_type: str):
    """Main function to run MCP servers with delegation pattern"""
    if mcp_type not in mcp_init_fns:
        available_types = ', '.join(mcp_init_fns.keys())
        raise ValueError(f"Unknown MCP server type: {mcp_type}. Available types: {available_types}")
    
    # Initialize MCP server parameters
    logger.info(f"Initializing {mcp_type} MCP server...")
    mcp_params = mcp_init_fns[mcp_type]()
    finalize_fn = mcp_fin_fns[mcp_type]
    
    try:
        logger.info(f"Starting {mcp_params.name} MCP server...")
        logger.info(f"Description: {mcp_params.description}")
        
        # Run the MCP server with appropriate transport
        transport = os.environ.get("MCP_TRANSPORT", "stdio")
        
        if transport.lower() == "http":
            # HTTP transport for local testing and deployment
            port = int(os.environ.get("PORT", 8000))
            host = os.environ.get("HOST", "0.0.0.0")
            logger.info(f"Starting MCP server on HTTP {host}:{port}")
            
            # Import asyncio and run HTTP server
            import asyncio
            asyncio.run(mcp_params.server.run_http_async(port=port, host=host))
        else:
            # stdio transport for local development and Claude Desktop subprocess mode
            logger.info("Starting MCP server with stdio transport")
            mcp_params.server.run()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise
    finally:
        # Clean up resources
        logger.info("Finalizing MCP server resources...")
        finalize_fn(mcp_params)
        logger.info("MCP server shutdown complete.")


if __name__ == "__main__":
    # Determine MCP server type from environment variable or command line argument
    mcp_type = None
    
    # Check environment variable first
    if "MCP_TYPE" in os.environ:
        mcp_type = os.environ["MCP_TYPE"]
        logger.info(f"Using MCP_TYPE from environment: {mcp_type}")
    
    # Check command line argument
    elif len(sys.argv) > 1:
        mcp_type = sys.argv[1]
        logger.info(f"Using MCP type from command line: {mcp_type}")
    
    # Default to incidents server
    else:
        mcp_type = "inc"
        logger.info(f"Using default MCP type: {mcp_type}")
    
    try:
        main(mcp_type)
    except ValueError as e:
        logger.error(str(e))
        available_types = ', '.join(mcp_init_fns.keys())
        logger.info(f"Usage: python mcp_server.py [MCP_TYPE] or set MCP_TYPE environment variable")
        logger.info(f"Available MCP types: {available_types}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)