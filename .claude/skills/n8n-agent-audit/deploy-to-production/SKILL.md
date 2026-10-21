---
name: deploy-to-production
description: Use when deploying a validated workflow to production. REQUIRES client approval. Creates backup, replicates changes and validates.
argument-hint: "workflow-name [--case case-id]"
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Deploy to Production

## Purpose
Deploy validated workflow from SANDBOX to production safely, with automatic backup, post-deploy validation, and complete documentation.

## When to Use
- After `/generate-case-report` and client approval
- ONLY after successful validation
- Last step in the correction flow

## CRITICAL WARNING

**THIS SKILL MODIFIES PRODUCTION**

MANDATORY prerequisites:
1. Case was analyzed (`/analyze-case`)
2. Workflow was modified in SANDBOX (`/modify-workflow`)
3. Fix was validated successfully (`/validate-fix`)
4. Executive report generated (`/generate-case-report`)
5. **Client APPROVED explicitly** (file `approved.txt` exists)

## Execution Flow

### 1. Verify Client Approval

```bash
if [ ! -f "docs/cases/${CASE_ID}/approved.txt" ]; then
  echo "ERROR: Client approval not found"
  echo "Client must create file: docs/cases/${CASE_ID}/approved.txt"
  echo ""
  echo "Suggested content:"
  echo "APPROVED"
  echo "Date: ${DATE}"
  echo "Approved by: [Client name]"
  exit 1
fi
```

### 2. Verify Prerequisites

- validation-result.md exists
- Validation was SUCCESSFUL

### 3. Confirm Deployment with User

```
PRODUCTION DEPLOYMENT

You are about to deploy changes to PRODUCTION.

**Case:** ${CASE_ID}
**Workflow:** ${WORKFLOW_NAME}
**Changes:** [Brief summary from fix-applied.md]

**Impact:** This change will affect real conversations with leads.

**Backup:** Automatic backup will be created.
**Rollback:** Available if problems arise.

Are you SURE you want to continue? (yes/no):
```

**IMPORTANT:** Wait for explicit "yes" (not "y").

### 4. Identify Production Workflow

Find production equivalent (without SANDBOX suffix) via n8n-MCP or ask user for production workflow ID.

### 5. Create Production Workflow Backup

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
# Save to: workflows/archive/production/${WORKFLOW_NAME}-${TIMESTAMP}.json
```

### 6. Get SANDBOX Changes

### 7. Apply Changes to Production

**IMPORTANT:** Do NOT replace entire workflow - only apply specific changes.

**Preserve:**
- Production credentials (NOT sandbox credentials)
- Production webhooks
- Production-specific configurations

### 8. Validate Updated Production Workflow

Delegate to `/n8n-validation`.

If validation fails:
```
PRODUCTION VALIDATION FAILED

Reverting changes automatically...
[Restore from backup]

Production workflow was NOT modified.
```

### 9. Update Changelog Automatically

Delegate to `/changelog-workflow`.

### 10. Generate Deployment Report

Save to: `docs/deployments/deploy-${WORKFLOW_NAME}-${DATE}.md`

Include: metadata, changes applied, pre-deploy validation, backup location, post-deploy validation, monitoring recommendations, rollback instructions.

### 11. Update Case Status

Mark as RESOLVED AND DEPLOYED.

### 12. Present Summary with Monitoring Instructions

```
PRODUCTION DEPLOYMENT SUCCESSFUL

**Case:** ${CASE_ID}
**Workflow:** ${WORKFLOW_NAME}
**Production ID:** ${PRODUCTION_ID}

**Backup:** workflows/archive/production/${WORKFLOW_NAME}-${TIMESTAMP}.json

POST-DEPLOYMENT MONITORING

**IMPORTANT:** Monitor real conversations for the next 24-48 hours.

**What to review:**
1. Conversations involving the modified functionality
2. Workflow executions in n8n
3. Errors or unexpected behaviors

**If problems detected:**
Rollback available from backup.

**Case ${CASE_ID} completely resolved**
```

## Security Protections

1. Client approval verification
2. Explicit "yes" confirmation required
3. Mandatory automatic backup
4. Mandatory post-deploy validation
5. Automatic rollback if validation fails
6. Production credential preservation
7. Complete deployment documentation

## Notes
- NEVER deploy without client approval
- ALWAYS create backup before modifying production
- ALWAYS validate after applying changes
- Apply ONLY specific changes, not full workflow replacement
- Preserve production credentials and configurations
- Document completely
- Post-deployment monitoring is CRITICAL
