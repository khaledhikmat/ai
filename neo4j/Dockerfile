# Neo4j Dockerfile for Railway Deployment
FROM neo4j:5.15-community

# Set environment variables for Neo4j configuration
ENV NEO4J_AUTH=neo4j/admin4neo4j
ENV NEO4J_dbms_default__database=neo4j
ENV NEO4J_dbms_memory_heap_initial__size=512m
ENV NEO4J_dbms_memory_heap_max__size=2G
ENV NEO4J_dbms_memory_pagecache_size=1G

# Listen on all interfaces (this is allowed)
ENV NEO4J_dbms_connector_bolt_listen__address=0.0.0.0:7687
ENV NEO4J_dbms_connector_http_listen__address=0.0.0.0:7474
ENV NEO4J_dbms_connector_https_listen__address=0.0.0.0:7473

# ❌ Do NOT set advertised address to 0.0.0.0 — we omit it entirely
# ENV NEO4J_dbms_connector_bolt_advertised__address=...
# ENV NEO4J_dbms_connector_http_advertised__address=...

# Security settings for Railway deployment
ENV NEO4J_dbms_security_procedures_unrestricted=jwt.*,apoc.*
ENV NEO4J_dbms_security_procedures_allowlist=jwt.*,apoc.*

# Performance and logging settings
ENV NEO4J_dbms_logs_query_enabled=INFO
ENV NEO4J_dbms_logs_query_threshold=0
ENV NEO4J_dbms_tx__log_rotation_retention__policy="1 days"
ENV NEO4J_db_tx_log_checkpoint_interval_time=15m
ENV NEO4J_server_config_strict__validation_enabled=false

# Create directories for data and logs
RUN mkdir -p /var/lib/neo4j/data \
    && mkdir -p /var/lib/neo4j/logs \
    && mkdir -p /var/lib/neo4j/import \
    && mkdir -p /var/lib/neo4j/plugins

# Set proper permissions
RUN chown -R neo4j:neo4j /var/lib/neo4j

# Expose Neo4j ports
EXPOSE 7474 7473 7687

# Health check to ensure Neo4j is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7474/ || exit 1

# Use the default Neo4j entrypoint
USER neo4j
CMD ["neo4j"]
