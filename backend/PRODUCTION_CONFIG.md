# MedMatch Production Deployment Configuration
# Use these settings when deploying to production

# ============== Environment Variables ==============
# Add to your production .env file

# MongoDB Connection Pooling
MONGO_POOL_SIZE=100
MONGO_MIN_POOL_SIZE=20

# Cache Settings  
CACHE_EXPIRE_SECONDS=300

# For production, add Redis:
# REDIS_URL=redis://your-redis-host:6379/0

# ============== Uvicorn Production Command ==============
# Replace the development command with this for production:

# Option 1: Multiple Workers (recommended for single server)
# uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4

# Option 2: With Gunicorn (better process management)
# gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# ============== Nginx Load Balancer Config ==============
# /etc/nginx/conf.d/medmatch.conf

upstream medmatch_backend {
    least_conn;  # Load balance to least connected server
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
    keepalive 64;
}

server {
    listen 80;
    server_name api.medmatch.com;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;
    
    location /api {
        proxy_pass http://medmatch_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    }
}

# ============== Docker Compose for Horizontal Scaling ==============
# docker-compose.prod.yml

version: '3.8'
services:
  api1:
    build: ./backend
    environment:
      - MONGO_URL=${MONGO_URL}
      - DB_NAME=${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
  
  api2:
    build: ./backend
    environment:
      - MONGO_URL=${MONGO_URL}
      - DB_NAME=${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api1
      - api2

volumes:
  redis_data:

# ============== Kubernetes Deployment ==============
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: medmatch-api
spec:
  replicas: 4
  selector:
    matchLabels:
      app: medmatch-api
  template:
    metadata:
      labels:
        app: medmatch-api
    spec:
      containers:
      - name: api
        image: medmatch/api:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_POOL_SIZE
          value: "50"
        - name: MONGO_MIN_POOL_SIZE
          value: "10"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 15
          periodSeconds: 20

---
apiVersion: v1
kind: Service
metadata:
  name: medmatch-api-service
spec:
  selector:
    app: medmatch-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: medmatch-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: medmatch-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

# ============== Redis Cache Configuration ==============
# To enable Redis caching, update server.py:

# from fastapi_cache.backends.redis import RedisBackend
# from redis import asyncio as aioredis
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Use Redis in production
#     redis = aioredis.from_url(os.environ.get('REDIS_URL', 'redis://localhost'))
#     FastAPICache.init(RedisBackend(redis), prefix="medmatch-cache")
#     yield
#     await redis.close()

# ============== Performance Tuning Checklist ==============
# 
# ✅ MongoDB Connection Pooling: 10-50 connections
# ✅ In-Memory Response Cache: 500 entries, 5min TTL
# ✅ Request Timing Headers: X-Process-Time-Ms
# ✅ Health Check Endpoint: /api/health
# ✅ Status Endpoint: /api/status
#
# For Production:
# □ Enable Redis caching
# □ Deploy multiple workers (4+)
# □ Set up load balancer
# □ Configure auto-scaling
# □ Enable CDN for static assets
# □ Set up monitoring (Prometheus/Grafana)
# □ Configure alerts for high latency/errors
