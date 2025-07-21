#!/usr/bin/env python3
"""
Production startup script for MCP server with health checks
"""

import os
import sys
import asyncio
import logging
import signal
from typing import Optional

from health_server import start_health_server
from mcp_server import main as mcp_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/mcp-server.log') if os.path.exists('/tmp') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


class MCPServerManager:
    def __init__(self):
        self.health_thread: Optional[object] = None
        self.mcp_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start both health server and MCP server"""
        try:
            # Start health check server
            health_port = int(os.environ.get('HEALTH_PORT', '8000'))
            self.health_thread = start_health_server(health_port)
            logger.info(f"Health server started on port {health_port}")
            
            # Get MCP server type
            mcp_type = os.environ.get("MCP_TYPE", "security")
            logger.info(f"Starting MCP server type: {mcp_type}")
            
            # Start MCP server in background task
            self.mcp_task = asyncio.create_task(mcp_main(mcp_type))
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
            
            logger.info("MCP Server Manager started successfully")
            
            # Wait for shutdown signal or MCP server completion
            await asyncio.gather(
                self.shutdown_event.wait(),
                self.mcp_task,
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            raise
        finally:
            await self.cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Initiate shutdown"""
        self.shutdown_event.set()
    
    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up MCP server resources...")
        
        if self.mcp_task and not self.mcp_task.done():
            self.mcp_task.cancel()
            try:
                await self.mcp_task
            except asyncio.CancelledError:
                pass
        
        logger.info("MCP server cleanup completed")


async def main():
    """Main entry point"""
    logger.info("Starting AI MCP Server Manager...")
    
    # Log environment info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"MCP_TYPE: {os.environ.get('MCP_TYPE', 'not set')}")
    logger.info(f"NEO4J_URI: {os.environ.get('NEO4J_URI', 'not set')}")
    
    manager = MCPServerManager()
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    
    logger.info("MCP Server Manager stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)