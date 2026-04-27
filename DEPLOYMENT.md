# 🚀 Deployment Guide

Complete guide for deploying the Deepfake Detection application to production.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 20+
- npm 10+
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd vision-mamba-deepfake
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Backend runs at: `http://localhost:8000`

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Step 1: Build Images

```bash
# Build all services
docker-compose build

# Or build individually
docker build -t deepfake-backend -f backend/Dockerfile .
docker build -t deepfake-frontend -f frontend/Dockerfile ./frontend
```

### Step 2: Run Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Step 3: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Access frontend
open http://localhost:3000
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: ECS Fargate (Recommended)

**Backend Deployment:**

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name deepfake-backend
```

2. **Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t deepfake-backend -f backend/Dockerfile .

# Tag image
docker tag deepfake-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepfake-backend:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/deepfake-backend:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "deepfake-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/deepfake-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/deepfake-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

4. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster deepfake-cluster \
  --service-name deepfake-backend \
  --task-definition deepfake-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**Frontend Deployment:**

1. **Build Production Bundle**
```bash
cd frontend
npm run build
```

2. **Create S3 Bucket**
```bash
aws s3 mb s3://deepfake-frontend
```

3. **Upload Files**
```bash
aws s3 sync dist/ s3://deepfake-frontend --acl public-read
```

4. **Configure CloudFront**
```bash
aws cloudfront create-distribution \
  --origin-domain-name deepfake-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

#### Option 2: EC2 Deployment

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow ports 22, 80, 443, 8000

2. **SSH into Instance**
```bash
ssh -i your-key.pem ubuntu@<instance-ip>
```

3. **Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. **Deploy Application**
```bash
# Clone repository
git clone <repository-url>
cd vision-mamba-deepfake

# Run with Docker Compose
docker-compose up -d
```

5. **Configure Nginx Reverse Proxy**
```bash
sudo apt install nginx -y

# Create nginx config
sudo nano /etc/nginx/sites-available/deepfake
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/deepfake /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Platform

#### Cloud Run Deployment

**Backend:**

1. **Build and Push to GCR**
```bash
# Configure gcloud
gcloud auth configure-docker

# Build image
docker build -t gcr.io/<project-id>/deepfake-backend -f backend/Dockerfile .

# Push image
docker push gcr.io/<project-id>/deepfake-backend
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy deepfake-backend \
  --image gcr.io/<project-id>/deepfake-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

**Frontend:**

1. **Build and Deploy to Firebase Hosting**
```bash
cd frontend
npm run build

# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy --only hosting
```

### Heroku Deployment

**Backend:**

```bash
# Login to Heroku
heroku login

# Create app
heroku create deepfake-backend

# Add container registry
heroku container:login

# Build and push
heroku container:push web -a deepfake-backend

# Release
heroku container:release web -a deepfake-backend

# Open app
heroku open -a deepfake-backend
```

**Frontend:**

```bash
# Create app
heroku create deepfake-frontend

# Add buildpack
heroku buildpacks:set heroku/nodejs -a deepfake-frontend

# Deploy
git subtree push --prefix frontend heroku main
```

---

## Production Checklist

### Backend

- [ ] **Environment Variables**
  - [ ] Set production API keys
  - [ ] Configure database URLs
  - [ ] Set secret keys

- [ ] **Security**
  - [ ] Configure CORS with specific origins
  - [ ] Enable HTTPS
  - [ ] Set up rate limiting
  - [ ] Implement authentication (if needed)
  - [ ] Add request validation

- [ ] **Performance**
  - [ ] Enable caching
  - [ ] Configure connection pooling
  - [ ] Set up CDN for static files
  - [ ] Optimize model loading

- [ ] **Monitoring**
  - [ ] Set up logging (CloudWatch, Stackdriver, etc.)
  - [ ] Configure error tracking (Sentry)
  - [ ] Add health check endpoints
  - [ ] Set up uptime monitoring

- [ ] **Scaling**
  - [ ] Configure auto-scaling
  - [ ] Set up load balancer
  - [ ] Implement queue for long-running tasks

### Frontend

- [ ] **Build Optimization**
  - [ ] Minify JavaScript and CSS
  - [ ] Enable tree shaking
  - [ ] Optimize images
  - [ ] Enable code splitting

- [ ] **Configuration**
  - [ ] Set production API URL
  - [ ] Configure analytics
  - [ ] Set up error tracking

- [ ] **Performance**
  - [ ] Enable gzip compression
  - [ ] Configure caching headers
  - [ ] Use CDN for assets
  - [ ] Optimize bundle size

- [ ] **SEO & Accessibility**
  - [ ] Add meta tags
  - [ ] Configure robots.txt
  - [ ] Add sitemap
  - [ ] Test accessibility

---

## Monitoring & Maintenance

### Logging

**Backend Logging:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

**Frontend Error Tracking:**

```typescript
// Install Sentry
npm install @sentry/react

// Configure in main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
});
```

### Health Checks

**Backend:**
```bash
curl http://your-api.com/health
```

**Frontend:**
```bash
curl http://your-app.com
```

### Backup Strategy

1. **Model Files**: Store in S3/GCS with versioning
2. **Configuration**: Keep in version control
3. **Database**: Regular automated backups (if applicable)

### Update Process

1. **Test locally**
2. **Deploy to staging**
3. **Run integration tests**
4. **Deploy to production**
5. **Monitor for errors**
6. **Rollback if needed**

### Scaling Considerations

**Horizontal Scaling:**
- Use load balancer
- Deploy multiple instances
- Implement session management

**Vertical Scaling:**
- Increase CPU/Memory
- Use GPU instances for faster inference
- Optimize model loading

---

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version
- Verify all dependencies installed
- Check model file exists
- Review logs for errors

**Frontend build fails:**
- Clear node_modules and reinstall
- Check Node.js version
- Verify environment variables

**API connection errors:**
- Check CORS configuration
- Verify API URL
- Check firewall rules
- Review network security groups

**Slow performance:**
- Enable caching
- Use CDN
- Optimize model inference
- Scale horizontally

---

## Support

For deployment issues:
1. Check logs
2. Review documentation
3. Open GitHub issue
4. Contact support

---

**Happy Deploying! 🚀**
