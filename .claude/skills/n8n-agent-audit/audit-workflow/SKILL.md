---
name: audit-workflow
description: Use when auditing an n8n workflow, validating configuration, identifying problems, verifying best practices.
argument-hint: "workflow-name"
user-invocable: true
allowed-tools: Read, Write, Grep, Glob
---

# Skill: Audit Workflow

## Purpose
Audit n8n workflows completely, validating technical configuration, verifying best practices, and analyzing business-specific aspects.

## When to Use
- After `/review-conversation` identified a problematic workflow
- Before modifying a workflow with `/modify-workflow`
- For periodic workflow reviews
- When configuration problems are suspected

## Execution Flow

### 1. Get Workflow Name

### 2. Get Complete Workflow using n8n-MCP

**IMPORTANT:** Use n8n-MCP tools, NOT direct JSON manipulation.

### 3. Delegate to Base n8n Skills

#### A. Technical Validation
Delegate to `/n8n-validation` for:
- Configuration error interpretation
- Expression syntax validation
- Connection verification between nodes
- Misconfigured node detection

#### B. Pattern Verification
Delegate to `/n8n-workflow-patterns` for:
- Architectural pattern verification
- Anti-pattern identification
- Structural improvement suggestions

### 4. Business-Specific Analysis

Review aspects that base skills don't cover:

#### A. AI Agent Prompts
- **Completeness:** Does it present the agent persona correctly? Includes qualification instructions? Has response examples?
- **Tone and voice:** Professional but approachable? Not too formal or casual?
- **Product knowledge:** Knows pricing ranges? Can reference products/services?

#### B. Lead Qualification Logic
For each criterion defined in business-context/:
- Is the question being asked?
- Is the response validated against business rules?
- Is data stored correctly in database?

#### C. Error Handling
- Error handling nodes present?
- Errors notified appropriately?
- Fallbacks for failing APIs?
- Technical errors hidden from leads?

#### D. Messaging Integration
- Messages sent correctly to channel?
- CRM status updated?
- Message format limits respected?

#### E. Database Storage
- Qualification data saved?
- Prepared queries used (avoid SQL injection)?
- DB connection errors handled?

### 5. Compare Against Best Practices

- Credentials not hardcoded
- Environment variables for configuration
- Descriptive node names
- Comments on complex nodes
- Deactivated for test workflows
- Webhooks with authentication if applicable
- Appropriate timeouts
- API retry limits

### 6. Generate Audit Report

Create file: `/docs/audits/${WORKFLOW_NAME}-${DATE}.md`

Include:
- Workflow information and metadata
- Technical validation results (from /n8n-validation)
- Pattern analysis results (from /n8n-workflow-patterns)
- Business-specific analysis (prompts, qualification, errors, integrations)
- Critical problems, warnings, suggestions
- Risk analysis with probability and impact
- Node-by-node analysis
- Immediate, short-term, and long-term recommendations

### 7. Present Summary

```
Workflow audit completed

**Workflow:** ${WORKFLOW_NAME}
**Overall status:** Good / Needs Attention / Critical

**Summary:**
- Critical problems: N
- Warnings: N
- Suggestions: N

**Next step:** [Recommendation based on findings]

**Full report:** /docs/audits/${WORKFLOW_NAME}-${DATE}.md
```

## Error Handling

- **n8n-MCP not responding:** Check configuration and credentials
- **Workflow not found:** Offer to list available workflows
- **Base skills unavailable:** Continue with business-specific audit only

## Dependencies
- **n8n-MCP:** For obtaining workflows
- **Base n8n skills:** `/n8n-validation`, `/n8n-workflow-patterns`
- **Business context:** For qualification criteria and product knowledge

## Notes
- ALWAYS use n8n-MCP for obtaining workflows
- ALWAYS delegate to base skills when available
- ALWAYS generate audit report
- NEVER modify workflows from this skill (use `/modify-workflow`)
- This skill is AUDIT ONLY, not correction
- Prioritize by severity: Critical > Warnings > Suggestions
