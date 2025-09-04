# Revisit ISO Standards Documentation

**Date**: 2025-08-31
**Priority**: To Be Determined
**Status**: Pending Review

## Context

The ISO standards documentation and implementation needs to be revisited to address the gap between having official metadata and actual requirement text.

## Current State

### What We Have
- **Official ISO Metadata**: Extracted from ISO Open Data (ODC-By v1.0 licensed)
  - Publication dates, editions, committee ownership
  - ICS codes and classification
  - 6 SMB-relevant standards metadata
  
### What We Don't Have
- Actual clause requirements ("The organization SHALL...")
- Specific control objectives from each clause
- Implementation requirements for each control
- Annex A controls (for ISO 27001)
- Detailed guidance on implementation
- Audit criteria and evidence requirements

## Action Items

- [ ] Review options for obtaining actual ISO standard requirements
- [ ] Consider purchasing necessary standards ($150-300 each from ISO.org)
- [ ] Evaluate alternatives like NIST CSF which is freely available
- [ ] Update system to clearly distinguish between metadata and requirements
- [ ] Implement proper extraction if/when full standards are obtained

## Technical Considerations

The system currently has:
- Neo4j structure ready to receive real ISO requirements
- UK regulatory compliance with 108 real obligations from 36 official documents
- Official ISO metadata for version tracking and committee information

## Next Steps

1. Determine which ISO standards are critical for production use
2. Budget for standard purchases if needed
3. Consider interim solutions using freely available frameworks
4. Update documentation to prevent confusion about data authenticity

---

*Note: This documentation clearly distinguishes between having ISO metadata (which we have) versus actual ISO requirements (which require purchasing the standards).*