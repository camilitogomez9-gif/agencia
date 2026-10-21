---
name: modify-workflow
description: Use when modifying an n8n workflow (prompts, logic, node configuration) safely with validation.
argument-hint: "workflow-name [--case case-id]"
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Modify Workflow

## Purpose
Modify n8n workflows safely with automatic backup, mandatory validation, and change documentation.

## When to Use
- **WITH case:** After `/analyze-case` identified necessary changes (MAIN FLOW)
- After `/audit-workflow` identified problems
- After `/validate-lead-scoring` suggested changes
- To implement corrections based on conversation analysis

## Case Integration

### If `--case [case-id]` is provided:
1. Read `analysis.md` to know WHAT to change
2. Apply specific changes documented in the analysis
3. Generate `fix-applied.md` automatically
4. Update case status

### If `--case` is NOT provided:
Legacy/manual mode - asks user what to modify.

## IMPORTANT: Security Principles

1. **ALWAYS use n8n-MCP** - NEVER edit JSON directly
2. **ALWAYS create backup before** - Export workflow to /workflows/archive/
3. **ALWAYS validate after** - Use n8n-MCP validation tools
4. **NEVER modify credentials** - Only node configuration
5. **CONFIRM before applying** - Show changes and request approval

## Execution Flow

### 1. Pre-requisite: Recommend Audit First

### 2. Get Workflow Name

### 2.5. Check for --case flag

If `--case` provided:
- Validate case directory exists
- Read analysis.md for changes to apply
- Confirm workflow matches what analysis recommends
- Apply changes from analysis automatically

### 3. Get Current Workflow using n8n-MCP

**NEVER manipulate JSON directly.**

### 4. Export Automatic Backup

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
# Save to: /workflows/archive/${WORKFLOW_NAME}-${TIMESTAMP}.json
```

### 5. Request or Confirm Modifications

Options:
1. Modify AI Agent prompt
2. Change node logic (IF, Switch, etc.)
3. Update integration configuration
4. Add new node
5. Delete node
6. Modify connections
7. Other

If audit exists, suggest changes based on findings.

### 6. Apply Modifications using n8n-MCP

**CRITICAL:** Use exclusively n8n-MCP tools.

- **Prompts:** Update promptTemplate, preserve rest
- **Logic:** Update conditions, preserve connections
- **New Nodes:** Create, configure, connect
- **Integrations:** Update config, NEVER modify credentials

### 7. Validate Modified Workflow

**MANDATORY:** Delegate to `/n8n-validation`.

### 8. Handle Validation Result

- **FAILS:** Revert from backup. NEVER leave invalid state.
- **PASSES:** Continue.

### 9-10. Update and Save Locally

### 11. Generate Change Documentation

#### With --case: Generate `fix-applied.md`

```markdown
# Modification Applied - Case ${CASE_ID}

**Date:** ${FULL_DATE}
**Modified workflow:** ${WORKFLOW_NAME} (${WORKFLOW_ID})

## Changes Made

### Node: ${NODE_NAME}
**Type:** ${NODE_TYPE}

#### Before
[Previous code/config]

#### After
[New code/config]

#### Explanation
[Why this change, based on analysis.md]

## Technical Validation
- Syntax correct
- Connections valid
- n8n expressions correct

## Backup
`/workflows/archive/${WORKFLOW_NAME}-${TIMESTAMP}.json`

## Next Step
`/validate-fix ${CASE_ID}`
```

#### Without --case: Generate generic diff document.

### 12-14. Update Status and Present Summary

## Rollback

```bash
# 1. Go to /workflows/archive/
# 2. Identify backup: ${WORKFLOW_NAME}-${TIMESTAMP}.json
# 3. Import via n8n-MCP or n8n UI
```

## Common Modification Types

1. **Update AI Agent Prompt** - Add instructions, improve tone, include examples
2. **Change Validation Logic** - Add range validations, change conditions
3. **Update Integrations** - Change endpoints, update field mappings
4. **Add Error Handling** - Catch errors, fallbacks, notifications

## Notes
- NEVER edit JSON directly
- ALWAYS create backup first
- ALWAYS validate after modifying
- ALWAYS test before production (`/test-workflow`)
- ALWAYS document changes (`/changelog-workflow`)
- Follow full flow: modify -> test -> changelog -> deploy
