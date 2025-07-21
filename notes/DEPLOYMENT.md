# MCP Server Deployment Guide

This guide covers deploying your AI MCP Server to various platforms, with a focus on Railway.

## 🚀 Railway Deployment (Recommended)

Railway is perfect for your MCP server because it supports Docker, provides managed databases, and has excellent GitHub integration.

### Step 1: Prepare Your Repository

1. **Ensure all files are in your repo:**
   ```bash
   git add Dockerfile docker-compose.yml railway.toml .dockerignore
   git add start_mcp_server.py health_server.py .env.example
   git commit -m "Add Docker deployment configuration"
   git push
   ```

### Step 2: Deploy to Railway

1. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "Deploy from GitHub repo"
   - Select your AI project repository

2. **Add Neo4j Database:**
   - In your Railway project dashboard
   - Click "+ New Service"
   - Choose "Database" → "Add Neo4j"
   - Note the connection details provided

3. **Configure Environment Variables:**
   - In your MCP server service settings
   - Go to "Variables" tab
   - Add these environment variables:

   ```bash
   # Required
   MCP_TYPE=security
   NEO4J_URI=<from_railway_neo4j_service>
   NEO4J_USERNAME=<from_railway_neo4j_service>
   NEO4J_PASSWORD=<from_railway_neo4j_service>
   
   # Optional (for GitLab integration)
   GITLAB_TOKEN=<your_gitlab_token>
   GITLAB_BASE_URL=https://gitlab.com
   REPO_TYPE=gitlab
   ```

4. **Deploy:**
   - Railway will automatically detect the Dockerfile
   - The deployment will start automatically
   - Monitor the build logs in the Railway dashboard

### Step 3: Access Your MCP Server

- Railway will provide a public URL like: `https://your-app.railway.app`
- Health check: `https://your-app.railway.app/health`
- Your MCP server will be running and accessible via the public URL

## 🐳 Local Development with Docker

### Quick Start
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your actual values

# Start with Docker Compose (includes Neo4j)
docker-compose up -d

# Check logs
docker-compose logs -f mcp-server

# Access services
# MCP Server: http://localhost:8000
# Neo4j Browser: http://localhost:7474
```

### Individual Docker Commands
```bash
# Build the image
docker build -t ai-mcp-server .

# Run just the MCP server (requires external Neo4j)
docker run -d \
  --name ai-mcp-server \
  -p 8000:8000 \
  -e NEO4J_URI=bolt://your-neo4j:7687 \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=your-password \
  -e MCP_TYPE=security \
  ai-mcp-server
```

## ☁️ Other Cloud Platforms

### Render
1. Connect your GitHub repo
2. Choose "Web Service"
3. Use Docker runtime
4. Set environment variables in Render dashboard
5. Add Render PostgreSQL database (modify code to support PostgreSQL)

### Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set stack to container: `heroku stack:set container`
4. Configure environment variables: `heroku config:set VAR=value`
5. Deploy: `git push heroku main`

### DigitalOcean App Platform
1. Create new app from GitHub
2. Choose your repository
3. Select Dockerfile
4. Configure environment variables
5. Add DigitalOcean Managed Database (PostgreSQL or MongoDB)

## 🔧 Production Configuration

### Environment Variables Required
```bash
# Core MCP Server
MCP_TYPE=security
HEALTH_PORT=8000

# Database (choose one)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=secure_password

# Optional: GitLab Integration
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_BASE_URL=https://your-gitlab.com
REPO_TYPE=gitlab
```

### Security Considerations
1. **Never commit .env files** - use .env.example instead
2. **Use strong passwords** for Neo4j
3. **Rotate API tokens** regularly
4. **Enable HTTPS** in production (Railway does this automatically)
5. **Monitor logs** for security issues

### Performance Optimization
1. **Resource Limits:**
   ```yaml
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 1G
         cpus: '0.5'
   ```

2. **Neo4j Tuning:**
   ```bash
   # Add to Neo4j environment
   NEO4J_dbms_memory_heap_initial__size=512m
   NEO4J_dbms_memory_heap_max__size=512m
   ```

## 📊 Monitoring & Health Checks

### Health Endpoints
- `GET /health` - Basic health status
- `GET /ready` - Readiness check

### Logging
- Logs are written to stdout (captured by Railway)
- Local logs: `/tmp/mcp-server.log` (in container)
- Use Railway's log streaming for real-time monitoring

### Metrics (Future Enhancement)
Consider adding:
- Prometheus metrics endpoint
- Database connection monitoring  
- Request rate limiting
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Neo4j Connection Failed:**
   ```bash
   # Check environment variables
   echo $NEO4J_URI
   
   # Test connection manually
   docker exec -it neo4j cypher-shell -u neo4j -p admin4neo4j
   ```

2. **Health Check Failing:**
   ```bash
   # Check if health server is running
   curl http://localhost:8000/health
   
   # Check container logs
   docker logs ai-mcp-server
   ```

3. **Railway Build Failing:**
   - Check Dockerfile syntax
   - Ensure requirements.txt is up to date
   - Verify all files are committed to git

4. **GitLab Authentication Issues:**
   - Verify GITLAB_TOKEN has correct permissions
   - Check token hasn't expired
   - Ensure GITLAB_BASE_URL is correct

### Getting Help
- Check Railway logs for deployment issues
- Use `docker-compose logs` for local debugging
- Monitor Neo4j query performance in browser UI
- Review MCP server logs for authentication errors

## 🔄 CI/CD Integration

### GitHub Actions (Example)
```yaml
name: Deploy to Railway
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway-deploy/railway-action@v2
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

This deployment setup provides a production-ready MCP server with proper health checks, monitoring, and scalability options.
EOF < /dev/null
