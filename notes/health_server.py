#!/usr/bin/env python3
"""
Simple health check server for MCP deployment
Runs alongside the MCP server to provide health endpoints
"""

import asyncio
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import logging

logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Simple health check
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "service": "ai-mcp-server",
                "version": "1.0.0"
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        elif self.path == '/ready':
            # Readiness check
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            ready_data = {
                "status": "ready",
                "timestamp": time.time()
            }
            
            self.wfile.write(json.dumps(ready_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        pass


def start_health_server(port=8000):
    """Start health check server in a separate thread"""
    def run_server():
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server started on port {port}")
        server.serve_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_health_server()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Health server stopped")