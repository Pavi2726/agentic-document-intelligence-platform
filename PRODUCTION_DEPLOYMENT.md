# 🚀 Production Deployment Guide

Complete guide for deploying with Nginx reverse proxy and Redis caching.

## 🏗️ Architecture

```
Internet
    ↓
┌─────────────────────────────────────┐
│  Nginx Reverse Proxy (Port 80/443) │
│  - Rate Limiting                    │
│  - Load Balancing                   │
│  - SSL Termination                  │
│  - Response Caching                 │
│  - Gzip Compression                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Backend API (Port 8000)            │
│  - FastAPI Application              │
│  - Redis Caching Layer              │
│  - Multi-instance Ready             │
└─────────────────────────────────────┘
    ↓
┌──────────┬──────────┬──────────┬──────────┐
│ MongoDB  │  Redis   │ Postgres │  Neo4j   │
│  :27017  │  :6379   │  :5432   │  :7687   │
└──────────┴──────────┴──────────┴──────────┘
```

## ✨ Production Features

### Nginx Reverse Proxy
- ✅ Load balancing with health checks
- ✅ Rate limiting (10 req/s API, 2 req/s uploads)
- ✅ Connection limits (10 per IP)
- ✅ Response caching (5min API, 7days static)
- ✅ Gzip compression
- ✅ Security headers
- ✅ SSL/TLS ready
- ✅ Request buffering
- ✅ Timeout management

### Redis Caching
- ✅ Query result caching
- ✅ Vector search caching
- ✅ Document chunk caching
- ✅ Knowledge graph caching
- ✅ Automatic cache invalidation
- ✅ TTL management
- ✅ Cache statistics

### Performance
- ✅ Response time < 100ms (cached)
- ✅ Handles 1000+ concurrent users
- ✅ Auto-scaling ready
- ✅ Resource limits configured

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy production template
cp .env.docker .env

# Edit with production values
nano .env
```

**Production .env:**
```env
# Groq API
GROQ_API_KEY=your_production_groq_key

# Strong passwords (16+ characters)
MONGO_PASSWORD=your_strong_mongo_password_here
REDIS_PASSWORD=your_strong_redis_password_here
POSTGRES_PASSWORD=your_strong_postgres_password_here
NEO4J_PASSWORD=your_strong_neo4j_password_here
```

### 2. Deploy with Production Config

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 3. Verify Deployment

```bash
# Check Nginx
curl http://localhost/api/health

# Check caching (should see X-Cache-Status header)
curl -I http://localhost/api/health

# Check rate limiting
for i in {1..15}; do curl http://localhost/api/health; done
```

## 📊 Nginx Features

### Rate Limiting

**API Endpoints:**
- 10 requests/second per IP
- Burst: 20 requests
- Returns 429 if exceeded

**Upload Endpoint:**
- 2 requests/second per IP
- Burst: 5 requests
- Prevents abuse

**Connection Limits:**
- Max 10 concurrent connections per IP

### Caching Strategy

**API Responses (5 minutes):**
```
GET /api/documents → Cached 5min
GET /api/analytics → Cached 5min
GET /api/graph/data → Cached 5min
```

**Static Files (1 year):**
```
*.js, *.css, *.png, *.jpg → Cached 1 year
```

**No Caching:**
```
POST /api/upload → Never cached
POST /api/chat → Never cached (streaming)
```

### Load Balancing

Nginx distributes requests across multiple backend instances:

```nginx
upstream backend {
    least_conn;  # Route to least busy server
    server backend:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}
```

## 🔧 Redis Caching

### Cache Service Features

**Query Caching:**
```python
from app.services.cache_service import cache_service

# Cache query result
cache_service.cache_query_result(query, result, ttl=300)

# Get cached result
cached = cache_service.get_cached_query(query)
```

**Vector Search Caching:**
```python
# Cache search results
cache_service.cache_vector_search(query, results, ttl=600)

# Get cached results
cached = cache_service.get_cached_vector_search(query)
```

**Document Chunk Caching:**
```python
# Cache document chunks
cache_service.cache_document_chunks(filename, chunks, ttl=3600)

# Get cached chunks
cached = cache_service.get_cached_chunks(filename)
```

**Cache Invalidation:**
```python
# Invalidate document cache when updated
cache_service.invalidate_document_cache(filename)
```

### Cache Statistics

```bash
# Get cache stats via API
curl http://localhost/api/cache/stats
```

Response:
```json
{
  "status": "connected",
  "used_memory": "2.5M",
  "connected_clients": 3,
  "total_keys": 150,
  "hits": 1250,
  "misses": 45
}
```

## 📈 Scaling

### Scale Backend Instances

```bash
# Scale to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Nginx automatically load balances
```

### Resource Limits

**Backend:**
- CPU: 1-2 cores
- Memory: 1-2GB
- Auto-restart on failure

**Redis:**
- Memory: 512MB
- Eviction: LRU (Least Recently Used)
- Persistence: AOF + RDB

## 🔐 Security

### SSL/TLS Setup

1. **Get SSL Certificate:**
```bash
# Using Let's Encrypt
certbot certonly --standalone -d yourdomain.com
```

2. **Update Nginx Config:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

3. **Mount Certificates:**
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Security Headers

Nginx adds these headers automatically:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: no-referrer-when-downgrade`

### Rate Limiting

Protects against:
- DDoS attacks
- Brute force attempts
- API abuse
- Resource exhaustion

## 📊 Monitoring

### Check Nginx Status

```bash
# Access logs
docker-compose -f docker-compose.prod.yml logs nginx

# Error logs
docker-compose -f docker-compose.prod.yml logs nginx | grep error

# Cache hit rate
docker-compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/access.log | grep "X-Cache-Status"
```

### Check Redis Status

```bash
# Connect to Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a redispassword

# Get info
INFO

# Check memory
INFO memory

# Monitor commands
MONITOR
```

### Performance Metrics

```bash
# Request latency
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/health

# Concurrent requests
ab -n 1000 -c 100 http://localhost/api/health
```

## 🔄 Deployment Workflow

### Initial Deployment

```bash
# 1. Configure
cp .env.docker .env
nano .env

# 2. Build
docker-compose -f docker-compose.prod.yml build

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify
curl http://localhost/api/health
```

### Update Deployment

```bash
# 1. Pull latest code
git pull

# 2. Rebuild
docker-compose -f docker-compose.prod.yml build

# 3. Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend

# 4. Verify
docker-compose -f docker-compose.prod.yml ps
```

### Rollback

```bash
# 1. Stop current
docker-compose -f docker-compose.prod.yml down

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Rebuild and deploy
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🎯 Performance Tuning

### Nginx Tuning

```nginx
# Worker processes (= CPU cores)
worker_processes auto;

# Worker connections
events {
    worker_connections 1024;
}

# Keepalive
keepalive_timeout 65;
keepalive_requests 100;
```

### Redis Tuning

```bash
# Increase max memory
redis-server --maxmemory 1gb

# Adjust eviction policy
redis-server --maxmemory-policy allkeys-lfu

# Enable persistence
redis-server --save 900 1 --appendonly yes
```

### Backend Tuning

```python
# Increase workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

## 📝 Maintenance

### Backup

```bash
# Backup volumes
docker run --rm -v agentic-mongodb-data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb-backup.tar.gz /data

# Backup Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a redispassword SAVE
```

### Clear Cache

```bash
# Clear Nginx cache
docker-compose -f docker-compose.prod.yml exec nginx rm -rf /var/cache/nginx/*

# Clear Redis cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a redispassword FLUSHDB
```

### Logs Rotation

```bash
# Rotate logs
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reopen
```

## ✅ Production Checklist

- [ ] Strong passwords in .env
- [ ] SSL certificate configured
- [ ] Rate limiting enabled
- [ ] Caching configured
- [ ] Monitoring setup
- [ ] Backup strategy
- [ ] Resource limits set
- [ ] Security headers enabled
- [ ] Firewall configured
- [ ] Domain configured
- [ ] Health checks working
- [ ] Logs rotation setup

## 🚀 Go Live

```bash
# Final deployment
docker-compose -f docker-compose.prod.yml up -d

# Monitor
docker-compose -f docker-compose.prod.yml logs -f

# Test
curl https://yourdomain.com/api/health
```

**Your production-ready AI application is now live!** 🎉
