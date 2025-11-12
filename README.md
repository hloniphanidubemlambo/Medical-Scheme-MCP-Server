# 🏥 Medical Scheme MCP Server

> A complete healthcare data integration platform connecting AI assistants to South African medical schemes and real healthcare data through FHIR standards.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![FHIR R4](https://img.shields.io/badge/FHIR-R4-orange.svg)](https://www.hl7.org/fhir/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

This platform bridges AI assistants with South African healthcare systems, enabling natural language interactions with medical schemes and real patient data.

**Key Capabilities:**
- 🤖 **AI Integration** - Connect ChatGPT, Claude, and other AI assistants to healthcare workflows
- 🏥 **Medical Schemes** - Discovery Health, GEMS, Medscheme support with benefit checks, authorizations, and claims
- 🌐 **Real Healthcare Data** - HAPI FHIR integration with actual patient records (no API keys required)
- ⚡ **Automated Workflows** - Complete patient processing from check-in to claim submission
- 📊 **Interactive Dashboard** - Web-based interface for testing and managing healthcare operations

## 🚀 Quick Start

### Prerequisites
- Windows 10/11, macOS, or Linux
- Python 3.8+ (tested with Python 3.14.0)
- Internet connection for FHIR integration

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd medical-scheme-mcp-server

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python start_server_simple.py
```

The server will start on `http://localhost:8000` with the following interfaces:
- 📊 **API Docs**: http://localhost:8000/docs
- 🏥 **Practice Dashboard**: http://localhost:8000/practice/dashboard
- 🔍 **Health Check**: http://localhost:8000/health

### Verify Installation

Test the FHIR integration with real healthcare data:

```bash
# Get authentication token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Test FHIR connectivity (use token from above)
curl -X GET "http://localhost:8000/fhir/integration/test" \
  -H "Authorization: Bearer <your-token>"

# Search real patients
curl -X GET "http://localhost:8000/fhir/patients/search?limit=3" \
  -H "Authorization: Bearer <your-token>"
```

Expected response includes real patient data from HAPI FHIR server:
```json
{
  "patients": [
    {"id": "7082689", "name": "Mayank Panwar", "gender": "male", "birthDate": "1974-12-25"},
    {"id": "7082691", "name": "Peter James Chalmers", "gender": "male", "birthDate": "1974-12-25"}
  ]
}
```

## 🌐 Features

### AI-Powered MCP Tools
Natural language interface for healthcare operations:
- Check patient benefits across medical schemes
- Request procedure authorizations
- Submit and track medical claims
- Execute complete patient workflows

### Real Healthcare Data Integration
- **HAPI FHIR Server**: Access real patient records from public FHIR R4 server
- **OpenEMR Support**: Connect to local clinic management systems
- **No API Keys Required**: Immediate access to test data
- **Standards Compliant**: Full FHIR R4 compatibility

### Medical Scheme Connectors
- **Discovery Health**: Benefit checks, pre-authorizations, claims
- **GEMS**: Government employee medical scheme operations
- **Medscheme**: Private medical scheme processing
- Mock connectors for testing, real API integration ready

### Web Interfaces

**Practice Dashboard** (`/practice/dashboard`)
- Interactive forms for benefit checks, authorizations, and claims
- Real-time FHIR data integration
- Quick access to common procedures and workflows

**API Documentation** (`/docs`)
- Interactive Swagger UI
- Test endpoints directly in browser
- JWT authentication support
- Complete API reference with examples

## 🔐 Authentication

The server uses JWT token-based authentication:

```bash
# Login to get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/mcp/tools" \
  -H "Authorization: Bearer <your-token>"
```

**Default Credentials:**
- Username: `admin`
- Password: `password123`

> ⚠️ Change default credentials before deploying to production

## 🏥 Supported Medical Schemes

| Scheme | Benefit Checks | Pre-Auth | Claims | Status | Data Source |
|--------|---------------|----------|--------|--------|-------------|
| **Discovery Health** | ✅ | ✅ | ✅ | ✅ | Mock (Real API Ready) |
| **GEMS** | ✅ | ✅ | ✅ | ✅ | Mock (Real API Ready) |
| **Medscheme** | ✅ | ✅ | ✅ | ✅ | Mock (Real API Ready) |
| **HAPI FHIR** ⭐ | ✅ | ✅ | ✅ | ✅ | **Real Data** |

### HAPI FHIR Integration
Access real healthcare data from the public FHIR R4 server:
- **Live Patient Records**: Real anonymized patient data
- **No Setup Required**: Works immediately without API keys
- **Standards Compliant**: Full FHIR R4 compatibility
- **Test Patients**: Mayank Panwar (7082689), Peter James Chalmers (7082691)
- **OpenEMR Ready**: Connect to local clinic systems

## 🔧 API Reference

### MCP Tools (AI Integration)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/tools` | GET | List all available MCP tools |
| `/mcp/tools/check_patient_benefits` | POST | Check patient benefits across schemes |
| `/mcp/tools/request_procedure_authorization` | POST | Request procedure authorization |
| `/mcp/tools/submit_medical_claim` | POST | Submit medical claim |
| `/mcp/tools/complete_patient_workflow` | POST | Execute complete patient workflow |

### Medical Scheme Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scheme/{scheme}/benefits/check` | POST | Check member benefits |
| `/scheme/{scheme}/authorization/request` | POST | Request pre-authorization |
| `/scheme/{scheme}/claim/submit` | POST | Submit claim |
| `/scheme/{scheme}/claim/{id}` | GET | Get claim status |

**Supported schemes:** `discovery`, `gems`, `medscheme`, `fhir`

### FHIR Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/fhir/integration/test` | GET | Test FHIR connectivity |
| `/fhir/patients/search` | GET | Search patients |
| `/fhir/patient/{id}` | GET | Get patient details |
| `/fhir/patient/{id}/claims` | GET | Get patient claims |

### Practice Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/practice/dashboard` | GET | Interactive web dashboard |
| `/practice/quick-benefit-check` | POST | Quick benefit verification |
| `/practice/procedures` | GET | Common procedure codes |
| `/practice/workflow-templates` | GET | Workflow templates |

### RIS Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ris/study/authorize` | POST | Authorize imaging study |
| `/ris/study/claim` | POST | Submit study claim |
| `/ris/billing/submit` | POST | Process billing data |

For detailed request/response schemas, visit the interactive API documentation at `/docs`.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_mock_connectors.py -v

# Run with coverage
pytest --cov=src tests/

# Test FHIR integration
pytest tests/test_fhir_integration.py -v
```

Test files included:
- `test_mock_connectors.py` - Medical scheme connector tests
- `test_fhir_integration.py` - FHIR integration tests
- `test_mcp_tools.py` - MCP tool functionality tests

## 🏗️ Architecture

```
medical-scheme-mcp-server/
├── src/
│   ├── server.py                    # FastAPI application entry point
│   ├── routes/
│   │   ├── scheme_routes.py         # Medical scheme endpoints
│   │   ├── mcp_routes.py            # MCP tool endpoints
│   │   ├── practice_routes.py       # Practice dashboard
│   │   ├── fhir_routes.py           # FHIR integration
│   │   └── ris_routes.py            # RIS/billing endpoints
│   ├── connectors/
│   │   ├── base_connector.py        # Abstract base connector
│   │   ├── discovery_connector.py   # Discovery Health
│   │   ├── gems_connector.py        # GEMS
│   │   ├── medscheme_connector.py   # Medscheme
│   │   └── fhir_connector.py        # FHIR integration
│   ├── models/
│   │   ├── claim.py                 # Claim data models
│   │   └── authorization.py         # Authorization models
│   ├── utils/
│   │   ├── auth.py                  # JWT authentication
│   │   └── logger.py                # Request/response logging
│   └── config/
│       ├── settings.py              # Configuration management
│       └── registry.py              # Connector registry
├── tests/                           # Test suite
├── examples/                        # Usage examples
├── requirements.txt                 # Python dependencies
└── docker-compose.yml              # Docker deployment
```

**Design Patterns:**
- **Connector Pattern**: Pluggable medical scheme integrations
- **Repository Pattern**: Data access abstraction
- **Middleware**: Request logging and authentication
- **Dependency Injection**: FastAPI's built-in DI system

## � Prvoject Status

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI Server | ✅ Production Ready | Fully functional REST API |
| FHIR Integration | ✅ Production Ready | Real healthcare data access |
| Mock Connectors | ✅ Complete | Discovery, GEMS, Medscheme |
| MCP Tools | ✅ Complete | AI assistant integration |
| Practice Dashboard | ✅ Complete | Web-based interface |
| Authentication | ✅ Complete | JWT token-based |
| Logging | ✅ Complete | Request/response tracking |
| RIS Integration | ✅ Complete | Imaging study workflows |
| Real API Integration | 🔄 Ready | Requires scheme API keys |
| Database Integration | 📋 Optional | For production persistence |
| Docker Support | ✅ Complete | Container deployment ready |

## 🔑 Real API Integration

The system is ready to connect to real medical scheme APIs. To switch from mock to production:

### Discovery Health
1. Register at [Discovery Developer Portal](https://developer.discovery.co.za)
2. Request test environment credentials
3. Add to `.env`: `DISCOVERY_API_KEY=your_key`
4. Update connector configuration

### GEMS
1. Contact GEMS IT department for API partnership
2. Complete compliance and security requirements
3. Obtain test/production credentials
4. Configure in `.env`: `GEMS_API_KEY=your_key`

### Medscheme
1. Contact Medscheme technical team
2. Complete integration assessment
3. Request API documentation and credentials
4. Configure in `.env`: `MEDSCHEME_API_KEY=your_key`

See `SWITCH_TO_REAL_APIS.md` for detailed migration guide.

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t medical-mcp-server .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run standalone container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name medical-mcp-server \
  medical-mcp-server
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Medical Scheme API Keys (optional - uses mock if not provided)
DISCOVERY_API_KEY=your_discovery_key
GEMS_API_KEY=your_gems_key
MEDSCHEME_API_KEY=your_medscheme_key

# Database (optional - for production persistence)
DATABASE_URL=postgresql://user:pass@localhost:5432/medical_mcp

# FHIR Configuration
FHIR_SERVER_URL=https://hapi.fhir.org/baseR4
OPENEMR_URL=http://localhost:8080  # Optional
```

### Production Checklist
- [ ] Change default admin credentials
- [ ] Set strong JWT secret key
- [ ] Configure HTTPS/TLS
- [ ] Set up database for persistence
- [ ] Configure CORS for your domain
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## 📝 Usage Examples

### Natural Language Queries (MCP Tools)

Use AI assistants to interact with the system:

```
"Check benefits for patient 7082689 on FHIR for consultation and MRI"
"Request authorization for Mayank Panwar on FHIR for urgent CT scan"
"Submit claim for patient consultation and blood work on Discovery"
"Complete workflow for new patient: check benefits, get auth, submit claim"
```

### Python Client

```python
import httpx
import asyncio

async def healthcare_workflow():
    async with httpx.AsyncClient() as client:
        # Authenticate
        auth_response = await client.post(
            "http://localhost:8000/auth/login",
            json={"username": "admin", "password": "password123"}
        )
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check benefits
        benefits = await client.post(
            "http://localhost:8000/scheme/discovery/benefits/check",
            json={
                "member_id": "DISC123456",
                "procedure_code": "MRI001"
            },
            headers=headers
        )
        print("Benefits:", benefits.json())
        
        # Search FHIR patients
        patients = await client.get(
            "http://localhost:8000/fhir/patients/search?limit=5",
            headers=headers
        )
        print("Patients:", patients.json())
        
        # Complete workflow
        workflow = await client.post(
            "http://localhost:8000/mcp/tools/complete_patient_workflow",
            params={
                "patient_name": "Sarah Johnson",
                "member_id": "DISC789012",
                "scheme_name": "discovery",
                "provider_id": "PROV001",
                "practice_name": "City Medical Centre",
                "workflow_type": "full_workflow"
            },
            json={
                "procedures": [{
                    "procedure_code": "CONS001",
                    "procedure_name": "General Consultation",
                    "estimated_cost": 500.00
                }]
            },
            headers=headers
        )
        print("Workflow:", workflow.json())

asyncio.run(healthcare_workflow())
```

### cURL Examples

```bash
# Authenticate
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}' \
  | jq -r '.access_token')

# Check benefits
curl -X POST "http://localhost:8000/scheme/discovery/benefits/check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "DISC123456",
    "procedure_code": "MRI001"
  }'

# Search FHIR patients
curl -X GET "http://localhost:8000/fhir/patients/search?limit=3" \
  -H "Authorization: Bearer $TOKEN"

# Request authorization
curl -X POST "http://localhost:8000/scheme/discovery/authorization/request" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "DISC123456",
    "procedure_code": "MRI001",
    "provider_id": "PROV001",
    "urgency": "routine"
  }'
```

### Interactive Dashboard

Access the web-based practice dashboard:
```
http://localhost:8000/practice/dashboard
```

Features:
- Quick benefit checks with dropdown selections
- Pre-authorization request forms
- Claim submission interface
- Real-time FHIR patient search
- Common procedure templates

## 📚 Documentation

- **[Complete Setup Guide](COMPLETE_SETUP_AND_USAGE_GUIDE.md)** - Detailed installation and configuration
- **[FHIR Integration](FHIR_INTEGRATION_GUIDE.md)** - Real healthcare data integration
- **[Testing Guide](TESTING_GUIDE.md)** - Testing procedures and verification
- **[MCP Tools](MCP_TOOLS_SUMMARY.md)** - AI assistant integration overview
- **[API Migration](SWITCH_TO_REAL_APIS.md)** - Switching from mock to real APIs

## �  Quick Reference

### Key URLs
- Practice Dashboard: http://localhost:8000/practice/dashboard
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- FHIR Test: http://localhost:8000/fhir/integration/test

### Default Credentials
- Username: `admin`
- Password: `password123`

### Test Patient IDs (FHIR)
- `7082689` - Mayank Panwar
- `7082691` - Peter James Chalmers
- `7082690` - Peter2 James2 Chalmers2

### Scheme Identifiers
- `discovery` - Discovery Health
- `gems` - GEMS
- `medscheme` - Medscheme
- `fhir` - HAPI FHIR (real data)

## 🔮 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Advanced analytics and reporting dashboard
- [ ] Multi-tenant support for healthcare providers
- [ ] Integration with additional medical schemes
- [ ] Mobile app companion
- [ ] Blockchain-based audit trail
- [ ] Machine learning for claim prediction
- [ ] HL7 v2 message support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass (`pytest tests/`)
- Code follows PEP 8 style guidelines
- New features include tests
- Documentation is updated

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: Check `/docs` endpoint for API reference
- **Examples**: See `examples/` directory for code samples
- **Community**: Join our discussions for questions and feedback

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [HAPI FHIR](https://hapi.fhir.org/) - Public FHIR test server
- [HL7 FHIR](https://www.hl7.org/fhir/) - Healthcare interoperability standards
- South African medical schemes for healthcare standards

---

**Built with ❤️ for the South African healthcare community**