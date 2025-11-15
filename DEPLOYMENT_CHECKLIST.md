# Deployment Checklist - Medical Scheme MCP Server v2.0

## Pre-Deployment Verification

### ✅ Code Quality
- [ ] All tests passing: `pytest tests/ -v`
- [ ] Code formatted: `black src tests`
- [ ] Linting clean: `flake8 src`
- [ ] Type checking: `mypy src --ignore-missing-imports`
- [ ] No security issues: `bandit -r src`

### ✅ Configuration
- [ ] `.env` file configured with production values
- [ ] `JWT_SECRET_KEY` changed from default
- [ ] `DEBUG=false` in production
- [ ] Database URL configured (if using database)
- [ ] CORS origins restricted to your domain
- [ ] Rate limiting configured appropriately

### ✅ Security
- [ ] HTTPS/TLS configured
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Audit logging functional
- [ ] Authentication working
- [ ] API keys secured (not in code)

### ✅ Testing
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Load testing completed
- [ ] Security testing done
- [ ] FHIR integration tested
- [ ] Medical scheme connectors tested

### ✅ Documentation
- [ ] README.md updated
- [ ] API documentation current
- [ ] Deployment guide written
- [ ] Runbook created
- [ ] Incident response plan documented

### ✅ Monitoring
- [ ] Audit logs configured
- [ ] Analytics dashboard accessible
- [ ] Error logging working
- [ ] Health check endpoints tested
- [ ] Alerting configured (optional)

## Production Environment Setup

### Server Requirements
```bash
# Minimum Requirements
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- OS: Ubuntu 20.04+ / Windows Server 2019+
- Python: 3.8+

# Recommended
- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB SSD
- Load balancer for high availability
```

### Installation Steps

#### 1. Clone Repository
```bash
git clone <repository-url>
cd medical-scheme-mcp-server
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy and edit .env file
cp .env.example .env
nano .env  # or your preferred editor

# Required changes:
# - JWT_SECRET_KEY: Generate strong key
# - DEBUG: Set to false
# - HOST: Set to 0.0.0.0 or specific IP
# - PORT: Set production port (usually 8000 or 443)
```

#### 5. Initialize Database (if using)
```bash
# Run migrations
alembic upgrade head

# Verify database connection
python -c "from src.database import engine; print('DB OK')"
```

#### 6. Test Configuration
```bash
# Run health check
python test_improvements.py

# Run full test suite
pytest tests/ -v
```

#### 7. Start Server
```bash
# Production mode with Uvicorn
uvicorn src.server:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn (recommended for production)
gunicorn src.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker Deployment

### Build Image
```bash
docker build -t medical-mcp-server:2.0.0 .
```

### Run Container
```bash
docker run -d \
  --name medical-mcp-server \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/audit_trail.log:/app/audit_trail.log \
  -v $(pwd)/analytics_data.json:/app/analytics_data.json \
  medical-mcp-server:2.0.0
```

### Docker Compose
```bash
docker-compose up -d
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# Basic health
curl https://your-domain.com/health

# Detailed health
curl https://your-domain.com/status

# FHIR integration
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/fhir/integration/test
```

### 2. Authentication Test
```bash
# Login
curl -X POST https://your-domain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Should return JWT token
```

### 3. Analytics Dashboard
```bash
# Access analytics
curl -H "Authorization: Bearer $TOKEN" \
  https://your-domain.com/analytics/dashboard
```

### 4. Audit Logs
```bash
# Check audit log is being written
tail -f audit_trail.log

# Verify log format
cat audit_trail.log | python -m json.tool | head -20
```

### 5. Rate Limiting
```bash
# Test rate limiting (should get 429 after 60 requests)
for i in {1..70}; do 
  curl -s -o /dev/null -w "%{http_code}\n" https://your-domain.com/health
done
```

## Monitoring Setup

### Log Files to Monitor
- `audit_trail.log` - All audit events
- `medical_mcp.log` - Application logs
- `analytics_data.json` - Analytics data
- System logs (varies by OS)

### Key Metrics to Track
- Request rate (requests/minute)
- Response time (ms)
- Error rate (%)
- Authentication failures
- Claim submission rate
- Authorization approval rate
- FHIR integration status

### Alerting Rules (Recommended)
```yaml
# Example alerting rules
- name: High Error Rate
  condition: error_rate > 5%
  action: Send alert to ops team

- name: Authentication Failures
  condition: failed_logins > 10 in 5 minutes
  action: Send security alert

- name: FHIR Integration Down
  condition: fhir_status != "connected"
  action: Send critical alert

- name: High Response Time
  condition: avg_response_time > 1000ms
  action: Send performance alert
```

## Backup Strategy

### What to Backup
- [ ] Database (if using)
- [ ] `audit_trail.log` (critical for compliance)
- [ ] `analytics_data.json`
- [ ] `.env` file (securely)
- [ ] Application code

### Backup Schedule
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup audit logs
cp audit_trail.log $BACKUP_DIR/

# Backup analytics
cp analytics_data.json $BACKUP_DIR/

# Backup database (if using)
pg_dump medical_mcp > $BACKUP_DIR/database.sql

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR.tar.gz s3://your-bucket/backups/
```

## Rollback Plan

### If Deployment Fails

#### 1. Quick Rollback
```bash
# Stop new version
docker stop medical-mcp-server

# Start previous version
docker start medical-mcp-server-old

# Or with systemd
systemctl stop medical-mcp-server
systemctl start medical-mcp-server-old
```

#### 2. Database Rollback (if needed)
```bash
# Restore from backup
pg_restore -d medical_mcp backup.sql

# Or rollback migrations
alembic downgrade -1
```

#### 3. Verify Rollback
```bash
# Check health
curl https://your-domain.com/health

# Check version
curl https://your-domain.com/ | grep version
```

## Security Hardening

### Server Level
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] SSH key-based authentication only
- [ ] Fail2ban installed and configured
- [ ] Regular security updates enabled
- [ ] Non-root user for application

### Application Level
- [ ] Strong JWT secret key (32+ characters)
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] CORS restricted to specific domains
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (security headers)

### Data Protection
- [ ] Database encryption at rest
- [ ] TLS 1.3 for data in transit
- [ ] Audit logs encrypted
- [ ] Regular security audits scheduled
- [ ] Incident response plan documented

## Compliance Verification

### POPIA Compliance
- [ ] Audit trail captures all data access
- [ ] Patient consent tracking implemented
- [ ] Data retention policy documented
- [ ] Data breach response plan ready
- [ ] Privacy policy published

### HIPAA Compliance (if applicable)
- [ ] PHI access logged
- [ ] Encryption in transit and at rest
- [ ] Access controls implemented
- [ ] Audit logs retained for 6 years
- [ ] Business associate agreements signed

## Performance Optimization

### Before Going Live
```bash
# Load testing
locust -f load_test.py --host=https://your-domain.com

# Database optimization
# - Add indexes on frequently queried fields
# - Optimize slow queries
# - Configure connection pooling

# Caching
# - Enable Redis for frequently accessed data
# - Configure CDN for static assets
# - Implement response caching
```

### Recommended Settings
```python
# Uvicorn workers (CPU cores * 2 + 1)
workers = 4

# Database connection pool
pool_size = 20
max_overflow = 10

# Rate limiting
requests_per_minute = 60

# Cache TTL
cache_ttl = 300  # 5 minutes
```

## Maintenance Schedule

### Daily
- [ ] Check audit logs for anomalies
- [ ] Review error logs
- [ ] Verify backups completed
- [ ] Monitor system resources

### Weekly
- [ ] Review analytics dashboard
- [ ] Check for security updates
- [ ] Test backup restoration
- [ ] Review performance metrics

### Monthly
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Update documentation

### Quarterly
- [ ] Compliance audit
- [ ] Disaster recovery test
- [ ] Security penetration test
- [ ] User feedback review

## Support Contacts

### Technical Support
- **Primary**: [Your Name/Team]
- **Email**: support@your-domain.com
- **Phone**: +27 XX XXX XXXX
- **Hours**: 24/7 for critical issues

### Escalation Path
1. Level 1: On-call engineer
2. Level 2: Senior engineer
3. Level 3: System architect
4. Level 4: CTO/Technical director

## Documentation Links

- **API Documentation**: https://your-domain.com/docs
- **User Guide**: README.md
- **Technical Guide**: IMPROVEMENTS_IMPLEMENTED.md
- **Quick Start**: QUICK_START_IMPROVEMENTS.md
- **Roadmap**: ROADMAP_REMAINING.md

## Sign-off

### Deployment Approval

- [ ] **Developer**: Code reviewed and tested
  - Name: ________________
  - Date: ________________

- [ ] **QA**: All tests passed
  - Name: ________________
  - Date: ________________

- [ ] **Security**: Security review completed
  - Name: ________________
  - Date: ________________

- [ ] **Operations**: Infrastructure ready
  - Name: ________________
  - Date: ________________

- [ ] **Management**: Deployment approved
  - Name: ________________
  - Date: ________________

---

**Deployment Date**: ________________
**Deployed By**: ________________
**Version**: 2.0.0
**Status**: ☐ Success ☐ Rollback Required
