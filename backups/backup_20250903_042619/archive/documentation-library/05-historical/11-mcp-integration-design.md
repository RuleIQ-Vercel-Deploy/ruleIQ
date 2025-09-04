# MCP Client Integration Design for ruleIQ

## Overview
This document outlines the integration of Model Context Protocol (MCP) client capabilities into ruleIQ's existing evidence collection architecture, focusing on automated third-party system connections for compliance evidence gathering.

## Current Architecture Analysis

### Existing Components
- **Integration Service** (`api/routers/integrations.py`) - Basic OAuth integration framework
- **Evidence Service** (`frontend/lib/api/evidence.service.ts`) - Evidence CRUD and automation
- **Base Integration** (`api/integrations/base/base_integration.py`) - Abstract integration class
- **Integration Configuration** (`database/integration_configuration.py`) - Database models

### Current Limitations
1. **Manual API Integration**: Each system requires custom implementation
2. **Limited Discovery**: No dynamic capability detection
3. **Basic Evidence Collection**: Static evidence types and collection patterns
4. **Fragmented Architecture**: Separate handling for each integration type

## MCP Client Integration Design

### 1. MCP Client Service Layer

```typescript
// frontend/lib/mcp/mcp-client.service.ts
export interface MCPEvidenceSource {
  name: string;
  provider: string;
  capabilities: string[];
  evidence_types: string[];
  compliance_frameworks: string[];
  automation_level: 'full' | 'partial' | 'manual';
  security_level: 'high' | 'medium' | 'basic';
}

export interface MCPEvidenceRequest {
  framework_id: string;
  control_ids: string[];
  evidence_types: string[];
  collection_mode: 'immediate' | 'scheduled' | 'streaming';
  quality_requirements: {
    completeness_threshold: number;
    recency_requirement: string; // e.g., "30d", "7d"
    validation_level: 'strict' | 'standard' | 'basic';
  };
}

export interface MCPEvidenceResult {
  evidence_id: string;
  source_system: string;
  collected_at: Date;
  evidence_type: string;
  control_mapping: string[];
  quality_score: number;
  raw_data: any;
  processed_data: any;
  audit_trail: MCPAuditEntry[];
}

class MCPEvidenceClient {
  private mcpTransport: MCPTransport;
  private connectedServers: Map<string, MCPServerConnection>;

  async discoverEvidenceSources(framework?: string): Promise<MCPEvidenceSource[]> {
    // Dynamic discovery of available MCP servers and their capabilities
    const sources: MCPEvidenceSource[] = [];
    
    for (const [serverName, connection] of this.connectedServers) {
      const capabilities = await connection.listTools();
      const evidenceCapabilities = capabilities.filter(tool => 
        tool.category === 'compliance' || tool.category === 'evidence'
      );
      
      if (evidenceCapabilities.length > 0) {
        sources.push({
          name: serverName,
          provider: connection.provider,
          capabilities: evidenceCapabilities.map(c => c.name),
          evidence_types: this.extractEvidenceTypes(evidenceCapabilities),
          compliance_frameworks: this.extractFrameworks(evidenceCapabilities),
          automation_level: this.determineAutomationLevel(evidenceCapabilities),
          security_level: connection.securityLevel
        });
      }
    }
    
    return sources;
  }

  async collectEvidence(request: MCPEvidenceRequest): Promise<MCPEvidenceResult[]> {
    const results: MCPEvidenceResult[] = [];
    
    // Intelligent source selection based on request requirements
    const optimalSources = await this.selectOptimalSources(request);
    
    // Parallel evidence collection with intelligent orchestration
    const collectionPromises = optimalSources.map(source => 
      this.collectFromSource(source, request)
    );
    
    const collectionResults = await Promise.allSettled(collectionPromises);
    
    // Process results and handle failures gracefully
    for (const result of collectionResults) {
      if (result.status === 'fulfilled') {
        results.push(...result.value);
      } else {
        // Log failure and attempt fallback collection
        await this.handleCollectionFailure(result.reason);
      }
    }
    
    return results;
  }

  async streamEvidenceCollection(
    request: MCPEvidenceRequest,
    onUpdate: (result: MCPEvidenceResult) => void
  ): Promise<void> {
    // Real-time streaming evidence collection
    const sources = await this.selectOptimalSources(request);
    
    for (const source of sources) {
      const connection = this.connectedServers.get(source.name);
      if (!connection) continue;
      
      // Stream evidence updates in real-time
      const stream = await connection.streamEvidence(request);
      
      for await (const evidenceUpdate of stream) {
        const processedResult = await this.processEvidenceResult(evidenceUpdate);
        onUpdate(processedResult);
      }
    }
  }

  private async selectOptimalSources(request: MCPEvidenceRequest): Promise<MCPEvidenceSource[]> {
    const availableSources = await this.discoverEvidenceSources(request.framework_id);
    
    // AI-driven source selection based on:
    // - Evidence type coverage
    // - Framework compliance
    // - Quality requirements
    // - Cost optimization
    // - Performance characteristics
    
    return availableSources.filter(source => {
      return source.compliance_frameworks.includes(request.framework_id) &&
             request.evidence_types.some(type => source.evidence_types.includes(type)) &&
             this.meetsQualityRequirements(source, request.quality_requirements);
    }).sort((a, b) => this.scoreSource(a, request) - this.scoreSource(b, request));
  }
}
```

### 2. Backend MCP Integration Service

```python
# services/mcp/mcp_evidence_service.py
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime, timedelta

class MCPServerType(Enum):
    AWS = "aws-mcp-server"
    GITHUB = "github-mcp-server"
    OKTA = "okta-mcp-server"
    CROWDSTRIKE = "crowdstrike-mcp-server"
    SPLUNK = "splunk-mcp-server"
    JIRA = "jira-mcp-server"

@dataclass
class MCPEvidenceCapability:
    tool_name: str
    evidence_types: List[str]
    frameworks: List[str]
    automation_level: str
    quality_score: float
    cost_factor: float

class MCPEvidenceOrchestrator:
    """Main orchestrator for MCP-based evidence collection"""
    
    def __init__(self):
        self.mcp_connections: Dict[str, MCPConnection] = {}
        self.evidence_mappings = self._load_evidence_mappings()
        
    async def initialize_connections(self, integration_configs: List[Dict]) -> None:
        """Initialize MCP connections based on user's integration configurations"""
        for config in integration_configs:
            if config.get('mcp_enabled', False):
                try:
                    connection = await self._create_mcp_connection(config)
                    self.mcp_connections[config['provider']] = connection
                    await self._validate_connection(connection)
                except Exception as e:
                    logger.error(f"Failed to initialize MCP connection for {config['provider']}: {e}")

    async def discover_evidence_capabilities(self, framework_id: str) -> List[MCPEvidenceCapability]:
        """Discover available evidence collection capabilities across all MCP servers"""
        capabilities = []
        
        for provider, connection in self.mcp_connections.items():
            try:
                server_tools = await connection.list_tools()
                
                for tool in server_tools:
                    if self._is_evidence_tool(tool):
                        capability = self._analyze_tool_capability(tool, framework_id)
                        if capability:
                            capabilities.append(capability)
                            
            except Exception as e:
                logger.error(f"Error discovering capabilities from {provider}: {e}")
                
        return capabilities

    async def collect_foundation_evidence(self, 
                                        business_profile: Dict,
                                        frameworks: List[str]) -> Dict[str, Any]:
        """Collect foundational evidence: Cloud, IAM, HRIS"""
        
        evidence_plan = await self._generate_foundation_plan(business_profile, frameworks)
        results = {
            'cloud_infrastructure': {},
            'identity_access': {},
            'human_resources': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow(),
                'frameworks': frameworks,
                'business_profile_id': business_profile.get('id')
            }
        }
        
        # Cloud Infrastructure Evidence
        if 'aws' in self.mcp_connections:
            results['cloud_infrastructure']['aws'] = await self._collect_aws_evidence(evidence_plan)
        if 'azure' in self.mcp_connections:
            results['cloud_infrastructure']['azure'] = await self._collect_azure_evidence(evidence_plan)
        if 'gcp' in self.mcp_connections:
            results['cloud_infrastructure']['gcp'] = await self._collect_gcp_evidence(evidence_plan)
            
        # Identity and Access Management Evidence
        if 'okta' in self.mcp_connections:
            results['identity_access']['okta'] = await self._collect_okta_evidence(evidence_plan)
        if 'azure_ad' in self.mcp_connections:
            results['identity_access']['azure_ad'] = await self._collect_azure_ad_evidence(evidence_plan)
            
        # Human Resources Evidence
        if 'bamboohr' in self.mcp_connections:
            results['human_resources']['bamboohr'] = await self._collect_hris_evidence(evidence_plan)
        if 'workday' in self.mcp_connections:
            results['human_resources']['workday'] = await self._collect_workday_evidence(evidence_plan)
            
        return results

    async def collect_security_evidence(self, 
                                      security_controls: List[str],
                                      frameworks: List[str]) -> Dict[str, Any]:
        """Collect security evidence: Endpoints, Vulnerabilities, SIEM (80% of SOC 2 & ISO 27001)"""
        
        results = {
            'endpoint_protection': {},
            'vulnerability_management': {},
            'siem_security': {},
            'network_security': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow(),
                'controls': security_controls,
                'frameworks': frameworks
            }
        }
        
        # Endpoint Protection Evidence
        if 'crowdstrike' in self.mcp_connections:
            results['endpoint_protection']['crowdstrike'] = await self._collect_crowdstrike_evidence(security_controls)
        if 'sentinelone' in self.mcp_connections:
            results['endpoint_protection']['sentinelone'] = await self._collect_sentinelone_evidence(security_controls)
            
        # Vulnerability Management Evidence
        if 'qualys' in self.mcp_connections:
            results['vulnerability_management']['qualys'] = await self._collect_qualys_evidence(security_controls)
        if 'rapid7' in self.mcp_connections:
            results['vulnerability_management']['rapid7'] = await self._collect_rapid7_evidence(security_controls)
            
        # SIEM and Security Monitoring Evidence
        if 'splunk' in self.mcp_connections:
            results['siem_security']['splunk'] = await self._collect_splunk_evidence(security_controls)
        if 'sentinel' in self.mcp_connections:
            results['siem_security']['sentinel'] = await self._collect_sentinel_evidence(security_controls)
            
        return results

    async def collect_sdlc_evidence(self, 
                                  development_controls: List[str],
                                  frameworks: List[str]) -> Dict[str, Any]:
        """Collect SDLC evidence: Code repos, CI/CD, Ticketing, Secrets"""
        
        results = {
            'code_repositories': {},
            'cicd_pipelines': {},
            'ticketing_systems': {},
            'secrets_management': {},
            'collection_metadata': {
                'timestamp': datetime.utcnow(),
                'controls': development_controls,
                'frameworks': frameworks
            }
        }
        
        # Code Repository Evidence
        if 'github' in self.mcp_connections:
            results['code_repositories']['github'] = await self._collect_github_evidence(development_controls)
        if 'gitlab' in self.mcp_connections:
            results['code_repositories']['gitlab'] = await self._collect_gitlab_evidence(development_controls)
            
        # CI/CD Pipeline Evidence
        if 'jenkins' in self.mcp_connections:
            results['cicd_pipelines']['jenkins'] = await self._collect_jenkins_evidence(development_controls)
        if 'github_actions' in self.mcp_connections:
            results['cicd_pipelines']['github_actions'] = await self._collect_github_actions_evidence(development_controls)
            
        # Ticketing and Change Management Evidence
        if 'jira' in self.mcp_connections:
            results['ticketing_systems']['jira'] = await self._collect_jira_evidence(development_controls)
        if 'servicenow' in self.mcp_connections:
            results['ticketing_systems']['servicenow'] = await self._collect_servicenow_evidence(development_controls)
            
        # Secrets Management Evidence
        if 'hashicorp_vault' in self.mcp_connections:
            results['secrets_management']['vault'] = await self._collect_vault_evidence(development_controls)
        if 'aws_secrets' in self.mcp_connections:
            results['secrets_management']['aws_secrets'] = await self._collect_aws_secrets_evidence(development_controls)
            
        return results

    async def stream_evidence_collection(self, 
                                       collection_plan: Dict,
                                       progress_callback) -> AsyncGenerator[Dict, None]:
        """Stream real-time evidence collection with progress updates"""
        
        total_tasks = len(collection_plan.get('tasks', []))
        completed_tasks = 0
        
        for task in collection_plan['tasks']:
            try:
                # Execute evidence collection task
                result = await self._execute_evidence_task(task)
                completed_tasks += 1
                
                # Yield progress update
                yield {
                    'type': 'progress',
                    'task_id': task['id'],
                    'completed': completed_tasks,
                    'total': total_tasks,
                    'percentage': (completed_tasks / total_tasks) * 100,
                    'result': result
                }
                
                # Call progress callback if provided
                if progress_callback:
                    await progress_callback(completed_tasks, total_tasks, result)
                    
            except Exception as e:
                yield {
                    'type': 'error',
                    'task_id': task['id'],
                    'error': str(e),
                    'completed': completed_tasks,
                    'total': total_tasks
                }

    # Private helper methods for specific system evidence collection
    async def _collect_aws_evidence(self, plan: Dict) -> Dict[str, Any]:
        """Collect AWS infrastructure and security evidence"""
        aws_connection = self.mcp_connections['aws']
        
        evidence = {
            'iam_policies': await aws_connection.call_tool('list_iam_policies'),
            'security_groups': await aws_connection.call_tool('list_security_groups'),
            'vpc_configuration': await aws_connection.call_tool('describe_vpcs'),
            'cloudtrail_logs': await aws_connection.call_tool('get_cloudtrail_events', {
                'start_time': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'event_types': ['iam', 'security', 'access']
            }),
            'compliance_reports': await aws_connection.call_tool('get_compliance_reports', {
                'frameworks': plan.get('frameworks', [])
            })
        }
        
        return evidence

    async def _collect_okta_evidence(self, plan: Dict) -> Dict[str, Any]:
        """Collect Okta identity and access management evidence"""
        okta_connection = self.mcp_connections['okta']
        
        evidence = {
            'user_accounts': await okta_connection.call_tool('list_users'),
            'group_memberships': await okta_connection.call_tool('list_groups'),
            'application_assignments': await okta_connection.call_tool('list_app_assignments'),
            'mfa_policies': await okta_connection.call_tool('get_mfa_policies'),
            'access_logs': await okta_connection.call_tool('get_system_logs', {
                'since': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'event_types': ['user.authentication', 'user.authorization', 'policy.evaluate']
            }),
            'compliance_reports': await okta_connection.call_tool('generate_compliance_report', {
                'frameworks': plan.get('frameworks', [])
            })
        }
        
        return evidence

    async def _collect_github_evidence(self, controls: List[str]) -> Dict[str, Any]:
        """Collect GitHub development and security evidence"""
        github_connection = self.mcp_connections['github']
        
        evidence = {
            'repositories': await github_connection.call_tool('list_repositories'),
            'branch_protection': await github_connection.call_tool('get_branch_protection_rules'),
            'security_policies': await github_connection.call_tool('get_security_policies'),
            'pull_request_reviews': await github_connection.call_tool('get_pr_review_history', {
                'since': (datetime.utcnow() - timedelta(days=90)).isoformat()
            }),
            'security_alerts': await github_connection.call_tool('get_security_alerts'),
            'workflow_runs': await github_connection.call_tool('get_workflow_runs', {
                'since': (datetime.utcnow() - timedelta(days=30)).isoformat()
            })
        }
        
        return evidence
```

### 3. Integration Configuration Updates

```python
# Enhanced integration configuration to support MCP
# database/models.py additions

class MCPIntegrationConfig(Base):
    __tablename__ = "mcp_integration_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    mcp_server_url = Column(String(255))
    mcp_server_type = Column(String(50))  # stdio, sse, http
    credentials = Column(Text)  # Encrypted MCP connection credentials
    capabilities = Column(JSON)  # Discovered MCP capabilities
    evidence_mappings = Column(JSON)  # Framework -> Evidence type mappings
    automation_settings = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_capability_discovery = Column(DateTime)
    last_evidence_collection = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mcp_integrations")
    evidence_collections = relationship("MCPEvidenceCollection", back_populates="integration_config")

class MCPEvidenceCollection(Base):
    __tablename__ = "mcp_evidence_collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_config_id = Column(UUID(as_uuid=True), ForeignKey("mcp_integration_configs.id"))
    framework_id = Column(String(50), nullable=False)
    control_ids = Column(JSON)
    evidence_types = Column(JSON)
    collection_status = Column(String(20))  # pending, in_progress, completed, failed
    collection_metadata = Column(JSON)
    evidence_results = Column(JSON)
    quality_scores = Column(JSON)
    collection_duration = Column(Integer)  # seconds
    error_details = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    integration_config = relationship("MCPIntegrationConfig", back_populates="evidence_collections")
```

### 4. API Endpoints for MCP Evidence Collection

```python
# api/routers/mcp_evidence.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/mcp/evidence", tags=["MCP Evidence Collection"])

@router.get("/sources/discover")
async def discover_evidence_sources(
    framework_id: str = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Discover available MCP evidence sources for the user"""
    orchestrator = MCPEvidenceOrchestrator()
    
    # Load user's MCP integration configurations
    user_configs = await get_user_mcp_configs(current_user.id, db)
    await orchestrator.initialize_connections(user_configs)
    
    # Discover available evidence capabilities
    capabilities = await orchestrator.discover_evidence_capabilities(framework_id)
    
    return {
        "framework_id": framework_id,
        "available_sources": len(capabilities),
        "capabilities": capabilities,
        "discovery_timestamp": datetime.utcnow()
    }

@router.post("/collect/foundation")
async def collect_foundation_evidence(
    request: FoundationEvidenceRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Collect foundation evidence: Cloud, IAM, HRIS"""
    
    # Validate user has required integrations
    required_integrations = ['aws', 'okta', 'bamboohr']  # Example
    user_integrations = await get_user_integrations(current_user.id, db)
    
    missing_integrations = [
        integration for integration in required_integrations 
        if integration not in [i.provider for i in user_integrations]
    ]
    
    if missing_integrations:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required integrations: {missing_integrations}"
        )
    
    # Start background evidence collection
    collection_id = str(uuid.uuid4())
    background_tasks.add_task(
        execute_foundation_evidence_collection,
        collection_id,
        current_user.id,
        request.business_profile,
        request.frameworks
    )
    
    return {
        "collection_id": collection_id,
        "status": "initiated",
        "estimated_duration": "5-15 minutes",
        "message": "Foundation evidence collection started"
    }

@router.post("/collect/security")
async def collect_security_evidence(
    request: SecurityEvidenceRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Collect security evidence: Endpoints, Vulnerabilities, SIEM"""
    
    collection_id = str(uuid.uuid4())
    background_tasks.add_task(
        execute_security_evidence_collection,
        collection_id,
        current_user.id,
        request.security_controls,
        request.frameworks
    )
    
    return {
        "collection_id": collection_id,
        "status": "initiated",
        "estimated_duration": "10-30 minutes",
        "message": "Security evidence collection started",
        "expected_coverage": "80% of SOC 2 & ISO 27001 control weight"
    }

@router.post("/collect/sdlc")
async def collect_sdlc_evidence(
    request: SDLCEvidenceRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Collect SDLC evidence: Code repos, CI/CD, Ticketing, Secrets"""
    
    collection_id = str(uuid.uuid4())
    background_tasks.add_task(
        execute_sdlc_evidence_collection,
        collection_id,
        current_user.id,
        request.development_controls,
        request.frameworks
    )
    
    return {
        "collection_id": collection_id,
        "status": "initiated",
        "estimated_duration": "8-20 minutes",
        "message": "SDLC evidence collection started",
        "benefits": "Airtight traceability for auditors"
    }

@router.get("/collect/{collection_id}/status")
async def get_collection_status(
    collection_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get status of evidence collection"""
    
    collection = await get_evidence_collection(collection_id, current_user.id, db)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return {
        "collection_id": collection_id,
        "status": collection.collection_status,
        "progress_percentage": calculate_progress_percentage(collection),
        "evidence_collected": len(collection.evidence_results or []),
        "quality_score": calculate_average_quality(collection),
        "started_at": collection.started_at,
        "estimated_completion": calculate_estimated_completion(collection),
        "current_activity": get_current_activity(collection)
    }

@router.get("/collect/{collection_id}/stream")
async def stream_collection_progress(
    collection_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Stream real-time progress of evidence collection"""
    
    async def event_stream():
        # Stream real-time updates using Server-Sent Events
        orchestrator = MCPEvidenceOrchestrator()
        
        async for update in orchestrator.stream_evidence_collection(
            collection_id, 
            lambda progress, total, result: None
        ):
            yield f"data: {json.dumps(update)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )
```

### 5. Frontend Integration Components

```typescript
// frontend/components/features/evidence/mcp-evidence-collector.tsx
export function MCPEvidenceCollector() {
  const [availableSources, setAvailableSources] = useState<MCPEvidenceSource[]>([]);
  const [selectedFramework, setSelectedFramework] = useState<string>('');
  const [collectionStatus, setCollectionStatus] = useState<'idle' | 'discovering' | 'collecting' | 'completed'>('idle');
  const [collectionProgress, setCollectionProgress] = useState<number>(0);
  const [evidenceResults, setEvidenceResults] = useState<any[]>([]);

  const discoverSources = async () => {
    setCollectionStatus('discovering');
    try {
      const response = await mcpEvidenceService.discoverSources(selectedFramework);
      setAvailableSources(response.capabilities);
    } catch (error) {
      toast.error('Failed to discover evidence sources');
    } finally {
      setCollectionStatus('idle');
    }
  };

  const startFoundationCollection = async () => {
    setCollectionStatus('collecting');
    setCollectionProgress(0);
    
    try {
      const response = await mcpEvidenceService.collectFoundationEvidence({
        framework: selectedFramework,
        business_profile: businessProfile
      });
      
      // Start real-time progress tracking
      const eventSource = new EventSource(
        `/api/mcp/evidence/collect/${response.collection_id}/stream`
      );
      
      eventSource.onmessage = (event) => {
        const update = JSON.parse(event.data);
        
        if (update.type === 'progress') {
          setCollectionProgress(update.percentage);
          setEvidenceResults(prev => [...prev, update.result]);
        } else if (update.type === 'completed') {
          setCollectionStatus('completed');
          eventSource.close();
        } else if (update.type === 'error') {
          toast.error(`Collection error: ${update.error}`);
        }
      };
      
    } catch (error) {
      toast.error('Failed to start evidence collection');
      setCollectionStatus('idle');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>MCP Evidence Collection</CardTitle>
          <CardDescription>
            Automated evidence collection from connected third-party systems
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="framework">Compliance Framework</Label>
              <Select value={selectedFramework} onValueChange={setSelectedFramework}>
                <SelectTrigger>
                  <SelectValue placeholder="Select framework" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="soc2_type2">SOC 2 Type II</SelectItem>
                  <SelectItem value="iso27001">ISO 27001</SelectItem>
                  <SelectItem value="gdpr">GDPR</SelectItem>
                  <SelectItem value="hipaa">HIPAA</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button 
              onClick={discoverSources} 
              disabled={!selectedFramework || collectionStatus === 'discovering'}
              className="w-full"
            >
              {collectionStatus === 'discovering' ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Discovering Sources...
                </>
              ) : (
                'Discover Available Evidence Sources'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {availableSources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Available Evidence Sources ({availableSources.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableSources.map((source) => (
                <div key={source.name} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{source.name}</h4>
                    <Badge variant={
                      source.automation_level === 'full' ? 'default' :
                      source.automation_level === 'partial' ? 'secondary' : 'outline'
                    }>
                      {source.automation_level}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    {source.evidence_types.length} evidence types
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {source.capabilities.slice(0, 3).map((capability) => (
                      <Badge key={capability} variant="outline" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                    {source.capabilities.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{source.capabilities.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Evidence Collection Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={startFoundationCollection}
              disabled={availableSources.length === 0 || collectionStatus === 'collecting'}
              className="h-20 flex-col"
            >
              <Cloud className="h-6 w-6 mb-2" />
              <span>Foundation</span>
              <span className="text-xs text-muted-foreground">Cloud, IAM, HRIS</span>
            </Button>
            
            <Button 
              onClick={() => startSecurityCollection()}
              disabled={availableSources.length === 0 || collectionStatus === 'collecting'}
              className="h-20 flex-col"
              variant="outline"
            >
              <Shield className="h-6 w-6 mb-2" />
              <span>Security</span>
              <span className="text-xs text-muted-foreground">80% of controls</span>
            </Button>
            
            <Button 
              onClick={() => startSDLCCollection()}
              disabled={availableSources.length === 0 || collectionStatus === 'collecting'}
              className="h-20 flex-col"
              variant="outline"
            >
              <GitBranch className="h-6 w-6 mb-2" />
              <span>SDLC</span>
              <span className="text-xs text-muted-foreground">Airtight traceability</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {collectionStatus === 'collecting' && (
        <Card>
          <CardHeader>
            <CardTitle>Collection Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Overall Progress</span>
                  <span>{Math.round(collectionProgress)}%</span>
                </div>
                <Progress value={collectionProgress} className="w-full" />
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Evidence Collected ({evidenceResults.length})</h4>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {evidenceResults.map((result, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">{result.evidence_type}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{result.source_system}</Badge>
                        <Badge variant={result.quality_score > 80 ? 'default' : 'secondary'}>
                          {result.quality_score}% quality
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

## Implementation Timeline

### Phase 1: Foundation (Week 1)
- **Day 1-2**: MCP client service implementation
- **Day 3-4**: Basic MCP connection management
- **Day 5-7**: Foundation evidence collection (Cloud, IAM, HRIS)

### Phase 2: Security Evidence (Week 2-3)
- **Day 8-14**: Security stack integrations (Endpoints, Vuln, SIEM)
- **Day 15-21**: Quality validation and optimization

### Phase 3: SDLC & Change (Week 4)
- **Day 22-30**: Development pipeline evidence collection

### Future Roadmap
- **Month 2**: Business & Scale integrations (HR training, Finance, Vendor, Collaboration, Backup)
- **Month 3**: ruleIQ MCP Server development
- **Month 4**: Advanced AI orchestration and autonomous collection

## Success Metrics
- **80% reduction** in manual evidence collection time
- **99% evidence coverage** for SOC 2 Type II and ISO 27001
- **Real-time compliance monitoring** with automated alerts
- **Airtight audit trails** with full system traceability
- **90% automation level** for routine compliance evidence

This MCP integration will transform ruleIQ from a manual compliance tool into an autonomous compliance automation platform, providing enterprise-grade evidence collection capabilities that auditors will love.