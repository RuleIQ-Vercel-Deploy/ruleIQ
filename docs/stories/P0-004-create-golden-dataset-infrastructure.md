# Story: Create Golden Dataset Infrastructure

## Story ID: P0-004
**Epic**: EPIC-2025-001
**Priority**: P0 - CRITICAL
**Sprint**: Immediate
**Story Points**: 3
**Owner**: Backend Team

## Status
**Current**: Draft
**Target**: Done
**Blocked By**: P0-001 (QueryCategory Enum)

## Story
**AS A** AI system developer  
**I WANT** a properly structured golden dataset infrastructure  
**SO THAT** the system can load, validate, and use reference datasets for compliance queries

## Background
Quinn's review found that while `services/ai/evaluation/data/` exists with a sample file, the required versioned golden dataset structure is missing. The system expects a `golden_datasets` directory with version subdirectories (e.g., v1.0.0) containing structured compliance data.

## Acceptance Criteria
1. ✅ **GIVEN** the evaluation data directory  
   **WHEN** the golden dataset infrastructure is created  
   **THEN** it must have the structure: `services/ai/evaluation/data/golden_datasets/v1.0.0/`

2. ✅ **GIVEN** the v1.0.0 dataset directory  
   **WHEN** populated with data  
   **THEN** it must contain:
   - `compliance_scenarios.json`
   - `evidence_cases.json`
   - `regulatory_qa_pairs.json`
   - `metadata.json` (version info)

3. ✅ **GIVEN** the golden dataset loader  
   **WHEN** loading datasets  
   **THEN** it must validate schema compliance and handle versioning

4. ✅ **GIVEN** a golden dataset  
   **WHEN** accessed by the system  
   **THEN** it must load within 500ms with proper caching

## Technical Requirements

### Directory Structure
```
services/ai/evaluation/data/
├── golden_datasets/
│   ├── v1.0.0/
│   │   ├── metadata.json
│   │   ├── compliance_scenarios.json
│   │   ├── evidence_cases.json
│   │   ├── regulatory_qa_pairs.json
│   │   └── README.md
│   └── current -> v1.0.0/  # Symlink to current version
└── sample_golden_dataset.json  # Keep for reference
```

### Metadata Schema
```json
{
  "version": "1.0.0",
  "created_at": "2025-01-12T00:00:00Z",
  "updated_at": "2025-01-12T00:00:00Z",
  "description": "Initial golden dataset for compliance validation",
  "datasets": {
    "compliance_scenarios": {
      "count": 50,
      "schema_version": "1.0",
      "description": "GDPR, CCPA, HIPAA compliance scenarios"
    },
    "evidence_cases": {
      "count": 30,
      "schema_version": "1.0",
      "description": "Evidence collection test cases"
    },
    "regulatory_qa_pairs": {
      "count": 100,
      "schema_version": "1.0",
      "description": "Question-answer pairs for regulatory queries"
    }
  },
  "validation": {
    "checksum": "sha256:...",
    "validated_at": "2025-01-12T00:00:00Z",
    "validator_version": "1.0"
  }
}
```

### Dataset Loader Implementation
```python
# services/ai/evaluation/golden_dataset_loader.py
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
import hashlib

class GoldenDatasetLoader:
    """Loads and manages versioned golden datasets"""
    
    def __init__(self, base_path: str = "services/ai/evaluation/data/golden_datasets"):
        self.base_path = Path(base_path)
        self.current_version = None
        self._cache = {}
    
    @lru_cache(maxsize=10)
    def load_dataset(
        self, 
        dataset_name: str, 
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load a specific dataset with caching"""
        version = version or self.get_current_version()
        cache_key = f"{version}:{dataset_name}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        dataset_path = self.base_path / version / f"{dataset_name}.json"
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset {dataset_name} not found in version {version}")
        
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        # Validate checksum
        if not self._validate_checksum(data, dataset_path):
            raise ValueError(f"Dataset {dataset_name} failed checksum validation")
        
        self._cache[cache_key] = data
        return data
    
    def get_current_version(self) -> str:
        """Get the current dataset version"""
        current_link = self.base_path / "current"
        if current_link.exists():
            return current_link.readlink().name
        
        # Fallback to latest version
        versions = sorted([d.name for d in self.base_path.iterdir() if d.is_dir()])
        if not versions:
            raise ValueError("No golden dataset versions found")
        return versions[-1]
    
    def _validate_checksum(self, data: Dict, path: Path) -> bool:
        """Validate dataset integrity"""
        content = json.dumps(data, sort_keys=True)
        checksum = hashlib.sha256(content.encode()).hexdigest()
        # Compare with stored checksum in metadata
        return True  # Implement actual validation
```

### Migration Script
```python
# scripts/migrate_golden_dataset.py
#!/usr/bin/env python3
"""Migrate sample dataset to versioned structure"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def migrate_golden_dataset():
    source = Path("services/ai/evaluation/data/sample_golden_dataset.json")
    target_dir = Path("services/ai/evaluation/data/golden_datasets/v1.0.0")
    
    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Load sample data
    with open(source, 'r') as f:
        sample_data = json.load(f)
    
    # Split into separate datasets
    datasets = {
        "compliance_scenarios": sample_data.get("scenarios", []),
        "evidence_cases": sample_data.get("evidence", []),
        "regulatory_qa_pairs": sample_data.get("qa_pairs", [])
    }
    
    # Save each dataset
    for name, data in datasets.items():
        with open(target_dir / f"{name}.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    # Create metadata
    metadata = {
        "version": "1.0.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "datasets": {
            name: {"count": len(data)} 
            for name, data in datasets.items()
        }
    }
    
    with open(target_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create symlink to current
    current_link = target_dir.parent / "current"
    if current_link.exists():
        current_link.unlink()
    current_link.symlink_to(target_dir.name)
    
    print(f"✅ Migrated golden dataset to {target_dir}")

if __name__ == "__main__":
    migrate_golden_dataset()
```

## Tasks/Subtasks
- [ ] Create `golden_datasets` directory structure
- [ ] Migrate sample dataset to v1.0.0 format
- [ ] Implement GoldenDatasetLoader class
- [ ] Add schema validation for each dataset type
- [ ] Create metadata.json with version info
- [ ] Implement caching mechanism
- [ ] Add CLI tool for dataset management
- [ ] Write migration documentation
- [ ] Test dataset loading performance

## Testing
```bash
# Test directory structure
test -d services/ai/evaluation/data/golden_datasets/v1.0.0

# Test dataset loading
python -c "
from services.ai.evaluation.golden_dataset_loader import GoldenDatasetLoader
loader = GoldenDatasetLoader()
scenarios = loader.load_dataset('compliance_scenarios')
assert len(scenarios) > 0
print('✅ Dataset loaded successfully')
"

# Performance test
time python -c "
from services.ai.evaluation.golden_dataset_loader import GoldenDatasetLoader
loader = GoldenDatasetLoader()
for _ in range(100):
    loader.load_dataset('compliance_scenarios')
"
```

## Definition of Done
- [ ] Directory structure created and verified
- [ ] Sample data migrated to v1.0.0
- [ ] GoldenDatasetLoader implemented with caching
- [ ] Schema validation working
- [ ] Load time < 500ms verified
- [ ] CLI tool functional
- [ ] Documentation updated
- [ ] All tests passing

## Notes
- Consider using Pydantic for schema validation
- May need to implement dataset versioning strategy
- Consider compression for large datasets
- Plan for future dataset updates and migrations

---
*Story created: 2025-01-12*
*Last updated: 2025-01-12*