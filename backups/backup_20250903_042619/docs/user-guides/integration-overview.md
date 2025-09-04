# Integration Overview

## Introduction

ruleIQ provides comprehensive integration capabilities to connect with your existing business systems, compliance tools, and workflows. This guide outlines available integration options and implementation approaches.

## Integration Types

### 1. API Integrations

**RESTful API Access**
- Full CRUD operations for all resources
- Real-time data synchronization
- Webhook support for event notifications
- Comprehensive OpenAPI documentation

**Key Endpoints:**
- `/api/v1/business-profiles` - Organization management
- `/api/v1/assessments` - Compliance assessments
- `/api/v1/evidence` - Document management
- `/api/v1/policies` - Policy generation and management
- `/api/v1/analytics` - Reporting and insights

### 2. Authentication Integration

**Single Sign-On (SSO)**
- SAML 2.0 support
- OpenID Connect (OIDC)
- Active Directory integration
- Google Workspace connectivity
- Microsoft Azure AD

**API Authentication**
- JWT bearer tokens
- API key authentication
- OAuth 2.0 flows
- Service account access

### 3. Document Management

**File Storage Integration**
- SharePoint Online
- Google Drive
- Dropbox Business
- Box Enterprise
- AWS S3
- Azure Blob Storage

**Document Workflow**
- Automatic evidence collection
- Version control synchronization
- Collaborative review processes
- Retention policy enforcement

### 4. Compliance Tools

**GRC Platform Integration**
- ServiceNow GRC
- MetricStream
- LogicGate Risk Cloud
- Resolver Integrated Risk Management
- RSA Archer

**Security Information Integration**
- Splunk SIEM
- Microsoft Sentinel
- IBM QRadar
- Elastic Security
- Rapid7 InsightIDR

## API Integration Guide

### Getting Started

**1. API Access Setup**
```bash
# Obtain API credentials from ruleIQ dashboard
# Account Settings > API Access > Generate New Key

curl -X POST https://api.ruleiq.com/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "api_secret": "your_api_secret"
  }'
```

**2. Authentication**
```javascript
// JavaScript example
const response = await fetch('https://api.ruleiq.com/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    api_key: 'your_api_key',
    api_secret: 'your_api_secret'
  })
});

const { access_token } = await response.json();
```

**3. Making API Calls**
```javascript
// Example: Fetch business profiles
const profiles = await fetch('https://api.ruleiq.com/api/v1/business-profiles', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});
```

### Common Integration Patterns

**Data Synchronization**
```python
# Python example: Sync employee data
import requests

class RuleIQSync:
    def __init__(self, api_key, api_secret):
        self.token = self.authenticate(api_key, api_secret)
    
    def sync_employees(self, employee_data):
        """Sync employee data with ruleIQ"""
        endpoint = "https://api.ruleiq.com/api/v1/employees"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        for employee in employee_data:
            response = requests.post(
                endpoint,
                headers=headers,
                json=employee
            )
            
            if response.status_code == 201:
                print(f"Employee {employee['name']} synced successfully")
```

**Webhook Integration**
```javascript
// Express.js webhook handler
app.post('/webhooks/ruleiq', (req, res) => {
  const { event_type, data } = req.body;
  
  switch(event_type) {
    case 'assessment.completed':
      handleAssessmentCompleted(data);
      break;
    case 'policy.updated':
      handlePolicyUpdated(data);
      break;
    case 'compliance.risk_detected':
      handleRiskDetected(data);
      break;
  }
  
  res.status(200).send('OK');
});
```

## SSO Configuration

### SAML 2.0 Setup

**1. Identity Provider Configuration**
```xml
<!-- SAML Assertion Example -->
<saml:Assertion>
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>user@company.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="role">
      <saml:AttributeValue>compliance_manager</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="department">
      <saml:AttributeValue>Legal</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

**2. Service Provider Settings**
- **Entity ID**: `https://api.ruleiq.com/saml`
- **ACS URL**: `https://api.ruleiq.com/saml/acs`
- **SLO URL**: `https://api.ruleiq.com/saml/slo`
- **Name ID Format**: `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress`

### Active Directory Integration

**LDAP Configuration**
```json
{
  "ldap_server": "ldap://company.local:389",
  "bind_dn": "CN=service-account,OU=Service Accounts,DC=company,DC=local",
  "search_base": "OU=Users,DC=company,DC=local",
  "user_filter": "(&(objectClass=user)(mail={email}))",
  "attribute_mapping": {
    "email": "mail",
    "first_name": "givenName",
    "last_name": "sn",
    "department": "department",
    "role": "title"
  }
}
```

## Document Management Integration

### SharePoint Online

**Setup Process:**
1. Register application in Azure AD
2. Grant necessary permissions
3. Configure document library mapping
4. Set up automated sync workflows

**Configuration Example:**
```json
{
  "sharepoint_config": {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "site_url": "https://yourcompany.sharepoint.com/sites/compliance",
    "document_library": "Evidence",
    "sync_interval": "hourly"
  }
}
```

### Google Drive Integration

**OAuth 2.0 Setup:**
```javascript
// Google Drive integration
const { google } = require('googleapis');

const oauth2Client = new google.auth.OAuth2(
  'your-client-id',
  'your-client-secret',
  'https://api.ruleiq.com/integrations/google/callback'
);

// Set up file monitoring
const drive = google.drive({ version: 'v3', auth: oauth2Client });

async function watchDocuments() {
  const response = await drive.files.watch({
    fileId: 'your-folder-id',
    requestBody: {
      id: 'unique-channel-id',
      type: 'web_hook',
      address: 'https://api.ruleiq.com/webhooks/google-drive'
    }
  });
}
```

## Compliance Tool Integration

### ServiceNow GRC

**Integration Components:**
- Risk record synchronization
- Control assessment mapping
- Incident correlation
- Reporting integration

**Configuration:**
```javascript
// ServiceNow REST API integration
const serviceNowConfig = {
  instance: 'your-instance.service-now.com',
  username: 'integration_user',
  password: 'secure_password',
  tables: {
    risks: 'sn_risk_risk',
    controls: 'sn_grc_control',
    assessments: 'sn_compliance_assessment'
  }
};

async function syncRisks() {
  const risks = await fetchFromRuleIQ('/api/v1/risks');
  
  for (const risk of risks) {
    await createServiceNowRecord('sn_risk_risk', {
      short_description: risk.title,
      description: risk.description,
      risk_level: risk.severity,
      state: risk.status
    });
  }
}
```

### Splunk SIEM Integration

**Log Forwarding:**
```bash
# Splunk forwarder configuration
[tcp://splunk-server:9997]
compressed = true

[monitor:///var/log/ruleiq/audit.log]
disabled = false
sourcetype = ruleiq_audit
index = compliance
```

**Custom Splunk App:**
```python
# Splunk custom command for ruleIQ data
import splunklib.client as client

class RuleIQCommand(GeneratingCommand):
    def generate(self):
        # Fetch data from ruleIQ API
        api_data = self.fetch_ruleiq_data()
        
        for record in api_data:
            yield {
                '_time': record['timestamp'],
                'event_type': record['type'],
                'user': record['user'],
                'action': record['action'],
                'resource': record['resource']
            }
```

## Workflow Automation

### Zapier Integration

**Available Triggers:**
- Assessment completed
- New risk identified
- Policy updated
- Compliance deadline approaching
- Evidence uploaded

**Example Zap:**
```javascript
// Trigger: Assessment completed in ruleIQ
// Action: Create task in Asana

{
  "trigger": {
    "event": "assessment.completed",
    "filter": "score < 75"
  },
  "action": {
    "service": "asana",
    "operation": "create_task",
    "data": {
      "name": "Address compliance gaps: {{assessment.name}}",
      "notes": "Compliance score: {{assessment.score}}%\nRecommendations: {{assessment.recommendations}}",
      "due_date": "{{date.add(days=30)}}"
    }
  }
}
```

### Microsoft Power Automate

**Flow Example:**
```json
{
  "trigger": {
    "type": "http_webhook",
    "url": "https://api.ruleiq.com/webhooks/power-automate"
  },
  "actions": {
    "condition": {
      "if": "@equals(triggerBody()?['event_type'], 'risk.critical')",
      "then": {
        "send_email": {
          "to": "compliance-team@company.com",
          "subject": "Critical Risk Identified",
          "body": "A critical compliance risk has been identified: @{triggerBody()?['data']?['title']}"
        }
      }
    }
  }
}
```

## Custom Integration Development

### SDK and Libraries

**Python SDK**
```python
# Install: pip install ruleiq-sdk
from ruleiq import RuleIQClient

client = RuleIQClient(
    api_key='your_api_key',
    api_secret='your_api_secret',
    environment='production'  # or 'sandbox'
)

# Fetch assessments
assessments = client.assessments.list(status='completed')

# Create new business profile
profile = client.business_profiles.create({
    'name': 'Acme Corp',
    'industry': 'Technology',
    'size': 'Medium',
    'location': 'United Kingdom'
})
```

**JavaScript SDK**
```javascript
// Install: npm install @ruleiq/sdk
import { RuleIQClient } from '@ruleiq/sdk';

const client = new RuleIQClient({
  apiKey: 'your_api_key',
  apiSecret: 'your_api_secret',
  environment: 'production'
});

// Stream real-time events
client.events.subscribe('all', (event) => {
  console.log('Received event:', event.type, event.data);
});
```

### Building Custom Connectors

**Connector Framework:**
```python
from ruleiq.connectors import BaseConnector

class CustomSystemConnector(BaseConnector):
    def __init__(self, config):
        super().__init__(config)
        self.system_api = CustomSystemAPI(config['api_url'])
    
    def sync_data(self):
        """Sync data from custom system to ruleIQ"""
        data = self.system_api.fetch_compliance_data()
        return self.transform_and_upload(data)
    
    def handle_webhook(self, payload):
        """Handle incoming webhook from custom system"""
        event = self.parse_webhook(payload)
        return self.forward_to_ruleiq(event)
```

## Security Considerations

### API Security
- Use HTTPS for all API communications
- Implement rate limiting (100 requests/minute)
- Rotate API keys regularly (quarterly)
- Monitor API usage and detect anomalies
- Implement proper error handling

### Data Protection
- Encrypt data in transit and at rest
- Implement proper access controls
- Log all data access and modifications
- Ensure GDPR compliance for data transfers
- Regular security assessments

### Integration Security
- Validate all webhook signatures
- Use secure authentication methods
- Implement timeout controls
- Monitor integration health
- Regular security reviews

## Monitoring and Troubleshooting

### Integration Health Monitoring

**Key Metrics:**
- API response times
- Success/failure rates
- Data synchronization lag
- Error frequency
- Resource utilization

**Monitoring Setup:**
```python
# Example monitoring setup
import logging
from prometheus_client import Counter, Histogram

api_requests = Counter('ruleiq_api_requests_total', 'Total API requests')
api_duration = Histogram('ruleiq_api_duration_seconds', 'API request duration')

@api_duration.time()
def make_api_request(endpoint, data):
    api_requests.inc()
    try:
        response = requests.post(endpoint, json=data)
        return response
    except Exception as e:
        logging.error(f"API request failed: {e}")
        raise
```

### Common Issues and Solutions

**Authentication Failures**
- Verify API credentials are correct
- Check token expiration
- Ensure proper scope permissions
- Validate network connectivity

**Data Sync Issues**
- Monitor rate limiting
- Check data format compliance
- Verify field mappings
- Review error logs

**Webhook Delivery Problems**
- Validate endpoint accessibility
- Check SSL certificate validity
- Verify webhook signature validation
- Monitor endpoint response times

## Getting Support

### Documentation Resources
- [API Reference](../api/) - Complete API documentation
- [Developer Setup](../developer/setup.md) - Development environment setup
- [Security Guide](../compliance/security-measures.md) - Security implementation details

### Support Channels
- **Developer Support**: api-support@ruleiq.com
- **Integration Consulting**: integrations@ruleiq.com
- **Technical Documentation**: docs@ruleiq.com
- **Community Forum**: https://community.ruleiq.com

### Professional Services
- Custom integration development
- Legacy system migration assistance
- Performance optimization consulting
- Security implementation review

---

*For detailed API documentation, see [API Reference](../api/)*
*For development setup, see [Developer Setup Guide](../developer/setup.md)*
*For security considerations, see [Security Measures](../compliance/security-measures.md)*