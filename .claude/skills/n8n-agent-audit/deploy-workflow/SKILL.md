---
name: deploy-workflow
description: Use when deploying a validated workflow to production in n8n self-hosted (legacy flow without case system).
argument-hint: [workflow-name]
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Deploy Workflow

## Purpose
Deploy validated and tested workflows to production in n8n safely, with pre-checks, final backup, and automatic documentation.

## When to Use
- After `/test-workflow` approved the modified workflow
- After `/changelog-workflow` documented the changes
- When workflow is ready for production use
- **NEVER** without prior testing

## CRITICAL Security Principles

1. **ONLY deploy TESTED workflows** - Verify `/test-workflow` passed
2. **ONLY deploy DOCUMENTED workflows** - Verify `/changelog-workflow` was run
3. **CONFIRM with user ALWAYS** - Show changes and request explicit approval
4. **Final BACKUP MANDATORY** - Before activating in production
5. **ACTIVATE workflow** - Ensure it's active after deployment
6. **DOCUMENT deployment** - Record when, what, and how

## Execution Flow

### 1. Get Workflow Name

### 2. Pre-Deployment Verifications (CRITICAL)

#### A. Verify Testing
Look for recent test in `/docs/tests/`:

If no recent test: **BLOCK DEPLOYMENT**. Testing is mandatory.

#### B. Verify Test Status
- REJECTED: BLOCK deployment
- APPROVED WITH OBSERVATIONS: WARN, let user decide
- APPROVED: Continue

#### C. Verify Changelog
Check `/docs/workflows/CHANGELOG-${WORKFLOW_NAME}.md` exists and is recent.

### 3. Confirm Deployment with User

Show: workflow name, changes summary, test results, impact assessment.
Wait for explicit confirmation.

### 4. Export Final Backup

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
# Save to: /workflows/archive/${WORKFLOW_NAME}-pre-deploy-${TIMESTAMP}.json
```

### 5. Update Workflow in n8n

1. Update via n8n-MCP
2. Verify saved correctly
3. **ACTIVATE workflow**

### 6. Verify Successful Deployment

1. Workflow exists and is active
2. Configuration correct
3. Credentials valid

If any check fails: automatic rollback from backup.

### 7. Update Changelog with Deployment Date

### 8. Generate Deployment Report

Save to: `/docs/deployments/deploy-${WORKFLOW_NAME}-${DATE}.md`

Include: metadata, changes deployed, pre-deploy validations, deployment process, post-deploy verification, impact assessment, monitoring recommendations, rollback instructions.

### 9. Remind User to Monitor

```
DEPLOYMENT COMPLETED SUCCESSFULLY

**Workflow:** ${WORKFLOW_NAME}
**Status:** Active in production

**Next 24 hours:**
1. Review conversations in CRM
2. Verify agent responds correctly
3. Monitor n8n logs for errors

**If problems detected:**
Backup available for immediate rollback.
```

## Security Protections

1. Testing mandatory (blocks deployment without it)
2. Explicit user confirmation
3. Final backup before deployment
4. Post-deployment verification
5. Automatic documentation
6. Workflow activation assurance

## Notes
- NEVER deploy without testing
- ALWAYS create backup
- ALWAYS confirm with user
- ALWAYS activate workflow
- ALWAYS document
- Monitor after deployment
- Full flow: review -> audit -> modify -> test -> changelog -> **deploy**
