# Neo4j Railway Deployment Guide

## 🚂 Railway Volume Mounting Strategy

Railway uses **persistent volumes** instead of local directory mounts. Here's how to handle your local volumes:

### Local vs Railway Volume Mapping

| Local Mount | Railway Volume | Purpose |
|-------------|----------------|---------|
| `$HOME/neo4j/data:/data` | `/var/lib/neo4j/data` → `neo4j-data` volume | Database storage |
| `$HOME/neo4j/logs:/logs` | `/var/lib/neo4j/logs` → `neo4j-logs` volume | Log files |

## 📦 Deployment Steps

### 1. Create Two Railway Services

#### Project:

```bash
# Create new Railway project from the root folder
railway login
railway init
# specify the name
```

#### Service 1: Neo4j Database
```bash
# Create new Railway service for Neo4j
# make sure you are linked to the project you just cretaed
railway link
cd neo4j-db
railway up
# in their infinite wisdom, there is no way to specify the service name, so the
# name defaults to the project name!!!
# you have to go to the railway dashboard to change the service name and change its network name in settings !!!
```

#### Service 2: MCP Server
```bash
# Create another service for your MCP server
# make sure you are linked to the project you just cretaed
railway link
cd src
railway up
# in their infinite wisdom, there is no way to specify the service name, so the
# name defaults to the project name!!!
# you have to go to the railway dashboard to change the service name and change its network name in settings !!!
# Use your existing Dockerfile and railway.toml
# Update environment variables to point to Neo4j service
railway up
```

### 2. Railway Volume Configuration

Railway automatically creates persistent volumes when you specify volume mounts:

```toml
# In railway-neo4j.toml
[deploy.volumeMounts]
"/var/lib/neo4j/data" = "neo4j-data"    # Persistent database storage
"/var/lib/neo4j/logs" = "neo4j-logs"    # Persistent log storage
```

### 3. Environment Variables for MCP Server

Update your MCP server's Railway environment variables:

```bash
# Neo4j connection (use Railway's internal networking)
NEO4J_URI=bolt://neo4j-db.railway.internal:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=admin4neo4j

# MCP Server configuration
MCP_TRANSPORT=http
PORT=$PORT  # Railway automatically sets this
```

### 4. Service Discovery

Railway provides internal DNS for service-to-service communication:

- **Neo4j Internal URL**: `neo4j-db.railway.internal:7687`
- **MCP Server Public URL**: `https://your-mcp-service.railway.app`

## 🔧 Railway CLI Commands

### Volume Management
```bash
# List volumes
railway volumes

# Check volume usage
railway logs

# Access service shell (for debugging)
railway shell
```

### Environment Variables
```bash
# Set environment variables
railway variables set NEO4J_URI=bolt://neo4j-db.railway.internal:7687
railway variables set NEO4J_USERNAME=neo4j
railway variables set NEO4J_PASSWORD=admin4neo4j

# List all variables
railway variables
```

### Service Linking
```bash
# Link services (if needed)
railway service

# Check service status
railway status
```

## 📊 Monitoring & Debugging

### Check Neo4j Health
```bash
# View Neo4j logs
railway logs --service neo4j-db

# Check if Neo4j is accessible
curl https://your-neo4j-service.railway.app:7474/
```

### Check MCP Server Health
```bash
# View MCP server logs
railway logs --service security-mcp-server

# Test MCP endpoints
curl https://your-mcp-service.railway.app/mcp/resources
```

## ⚠️ Important Notes

### Volume Persistence
- Railway volumes are **persistent** across deployments
- Data survives container restarts and redeployments
- Volumes are backed up automatically by Railway

### Local Development vs Railway
- **Local**: Direct directory mounts (`$HOME/neo4j/data:/data`)
- **Railway**: Named persistent volumes (`neo4j-data` volume)
- **Migration**: Data needs to be exported/imported between environments

### Resource Limits
- Railway has memory/CPU limits per service
- Neo4j memory settings should respect Railway's limits:
  ```env
  NEO4J_dbms_memory_heap_max__size=1G  # Adjust based on Railway plan
  NEO4J_dbms_memory_pagecache_size=512m
  ```

### Security
- Neo4j is accessible internally via `railway.internal` domain
- External access requires Railway's public networking (if needed)
- Use strong passwords in production

## 🔄 Data Migration (Local → Railway)

If you need to migrate existing local Neo4j data:

1. **Export from local Neo4j**:
   ```bash
   neo4j-admin dump --database=neo4j --to=/path/to/backup.dump
   ```

2. **Import to Railway Neo4j**:
   ```bash
   # Copy dump file to Railway service
   railway shell --service neo4j-db
   neo4j-admin load --database=neo4j --from=/path/to/backup.dump --force
   ```

This setup provides persistent storage for your Neo4j data while deployed on Railway! 🚀