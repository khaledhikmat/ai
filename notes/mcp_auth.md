Great question! Adding authentication to your MCP server is crucial for production deployments. Here
   are several approaches you can implement, ranging from simple to enterprise-grade:

  🔐 Authentication Strategies

  1. API Key Authentication (Simplest)

  # Add to your MCP server
  @mcp.middleware()
  async def api_key_auth(request, call_next):
      api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization",
  "").replace("Bearer ", "")

      valid_keys = os.environ.get("MCP_API_KEYS", "").split(",")
      if api_key not in valid_keys:
          return {"error": "Invalid API key", "status": 401}

      return await call_next(request)

  2. JWT Token Authentication (Recommended)

  import jwt
  from datetime import datetime, timedelta

  class JWTAuth:
      def __init__(self, secret_key: str):
          self.secret_key = secret_key

      def generate_token(self, user_id: str, roles: List[str]) -> str:
          payload = {
              "user_id": user_id,
              "roles": roles,
              "exp": datetime.utcnow() + timedelta(hours=24),
              "iat": datetime.utcnow()
          }
          return jwt.encode(payload, self.secret_key, algorithm="HS256")

      def verify_token(self, token: str) -> dict:
          try:
              return jwt.decode(token, self.secret_key, algorithms=["HS256"])
          except jwt.ExpiredSignatureError:
              raise AuthError("Token expired")
          except jwt.InvalidTokenError:
              raise AuthError("Invalid token")

  3. OAuth2 Integration (Enterprise)

  # Integration with Auth0, GitHub, Google, etc.
  from authlib.integrations.starlette_client import OAuth

  oauth = OAuth()
  oauth.register(
      name='github',
      client_id=os.environ.get('GITHUB_CLIENT_ID'),
      client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
      server_metadata_url='https://api.github.com/.well-known/oauth_2_0',
  )

  4. Role-Based Access Control (RBAC)

  class RoleManager:
      ROLES = {
          "admin": ["create", "read", "update", "delete", "manage_users"],
          "security_analyst": ["read", "create_incidents", "update_incidents"],
          "viewer": ["read"],
          "incident_manager": ["read", "create_incidents", "update_incidents", "assign_officers"]
      }

      @staticmethod
      def has_permission(user_roles: List[str], required_permission: str) -> bool:
          for role in user_roles:
              if required_permission in RoleManager.ROLES.get(role, []):
                  return True
          return False

  # Example usage in MCP tools
  @mcp.tool()
  @require_permission("create_incidents")
  def create_incident(...):
      # Only users with roles that have "create_incidents" permission can access
      pass

  🏗️ Implementation Architecture

  Proposed Auth Service Layer

  # service/auth/typex.py
  class IAuthService(Protocol):
      async def authenticate(self, token: str) -> AuthUser
      async def authorize(self, user: AuthUser, permission: str) -> bool
      async def create_token(self, user_id: str, roles: List[str]) -> str

  # service/auth/jwt.py
  class JWTAuthService(IAuthService):
      # Implementation with JWT, user storage, role management
      pass

  # mcp/incidents/server.py
  @dataclass
  class SecurityMCPDeps:
      security_service: ISecurityKnowledgeBaseService
      auth_service: IAuthService  # Add auth service

  MCP Server Integration

  # Enhanced MCP server with auth middleware
  @mcp.middleware()
  async def auth_middleware(request, call_next):
      # Skip auth for health checks
      if request.path in ["/health", "/ready"]:
          return await call_next(request)

      try:
          token = extract_token(request)
          user = await deps.auth_service.authenticate(token)
          request.state.user = user
          return await call_next(request)
      except AuthError as e:
          return {"error": str(e), "status": 401}

  @mcp.tool()
  def create_incident(...):
      user = request.state.user
      if not deps.auth_service.authorize(user, "create_incidents"):
          return {"error": "Insufficient permissions", "status": 403}

      # Proceed with incident creation
      pass

  🌐 Client-Side Integration

  Claude Desktop Configuration

  {
    "mcpServers": {
      "security-kb": {
        "command": "python",
        "args": ["/path/to/mcp_server.py", "security"],
        "env": {
          "MCP_AUTH_TOKEN": "your-jwt-token-here"
        }
      }
    }
  }

  Web Dashboard for Token Management

  # Optional: Simple web interface for token generation
  @app.route("/auth/login", methods=["POST"])
  async def login():
      # Validate credentials
      # Generate JWT token
      # Return token to user
      pass

  @app.route("/auth/tokens", methods=["GET"])
  async def list_tokens():
      # Show user's active tokens
      # Allow token revocation
      pass

  🔧 Implementation Levels

  Level 1: Quick API Key (1-2 hours)

  - Environment variable with comma-separated API keys
  - Simple header validation
  - Good for MVP/testing

  Level 2: JWT with Roles (1 day)

  - JWT token generation/validation
  - Role-based permissions
  - Token expiration handling
  - Production-ready for small teams

  Level 3: Full OAuth2 + RBAC (2-3 days)

  - OAuth2 integration (GitHub/Google/Auth0)
  - Comprehensive role management
  - User management interface
  - Audit logging
  - Enterprise-ready

  Level 4: Enterprise Auth (1 week)

  - SAML/SSO integration
  - Advanced RBAC with dynamic permissions
  - Multi-tenant support
  - Comprehensive audit trails
  - Compliance features

  📊 Security Considerations

  Token Storage & Management

  # Environment variables for auth
  MCP_JWT_SECRET=your-super-secret-key-here
  MCP_TOKEN_EXPIRY_HOURS=24
  MCP_ALLOWED_ROLES=admin,security_analyst,viewer
  MCP_REQUIRE_AUTH=true  # Disable for development

  Security Headers

  # Add security middleware
  @mcp.middleware()
  async def security_headers(request, call_next):
      response = await call_next(request)
      response.headers.update({
          "X-Content-Type-Options": "nosniff",
          "X-Frame-Options": "DENY",
          "X-XSS-Protection": "1; mode=block",
          "Strict-Transport-Security": "max-age=31536000"
      })
      return response

  🎯 Recommended Approach

  For your use case, I'd suggest Level 2 (JWT with Roles):

  1. JWT tokens for stateless authentication
  2. Role-based permissions for different user types
  3. Environment-based configuration for flexibility
  4. Integration with your existing service layer

  This provides enterprise-grade security while remaining manageable and fitting perfectly with your
  delegation architecture.

  Would you like me to implement any of these approaches when you're ready? I can create the auth
  service layer and integrate it with your existing MCP server structure.