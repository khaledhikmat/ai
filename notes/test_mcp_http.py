#!/usr/bin/env python3
"""
Test script to properly test MCP HTTP endpoints
"""

import requests
import json
import time

def test_mcp_endpoints():
    """Test various MCP HTTP endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MCP Server HTTP Endpoints")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Test 2: MCP Resources endpoint
    print("\n2️⃣ Testing MCP resources endpoint...")
    try:
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        response = requests.get(f"{base_url}/mcp/resources", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: MCP Tools endpoint  
    print("\n3️⃣ Testing MCP tools endpoint...")
    try:
        headers = {
            "Accept": "text/event-stream", 
            "Cache-Control": "no-cache"
        }
        response = requests.get(f"{base_url}/mcp/tools", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 4: Try JSON-RPC style request
    print("\n4️⃣ Testing JSON-RPC request...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {}
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(f"{base_url}/mcp", json=payload, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 5: Check available paths
    print("\n5️⃣ Testing common paths...")
    paths_to_test = [
        "/health",
        "/docs", 
        "/openapi.json",
        "/mcp",
        "/mcp/",
        "/resources",
        "/tools"
    ]
    
    for path in paths_to_test:
        try:
            response = requests.get(f"{base_url}{path}", timeout=2)
            status = "✅" if response.status_code < 400 else "❌"
            print(f"   {status} {path}: {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"   ❌ {path}: Connection failed")

if __name__ == "__main__":
    print("Make sure your MCP server is running with:")
    print("export MCP_TRANSPORT=http && python mcp_server.py security")
    print("\nWaiting 3 seconds for you to start the server...")
    time.sleep(3)
    
    test_mcp_endpoints()