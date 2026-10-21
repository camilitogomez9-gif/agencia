---
name: validate-lead-scoring
description: Use when validating that the agent is correctly scoring/qualifying leads according to defined business criteria.
user-invocable: true
allowed-tools: Read, Write, Grep
---

# Skill: Validate Lead Scoring

## Purpose
Validate that the AI agent is correctly qualifying leads according to the business criteria defined in your business-context files.

## When to Use
- When agent qualification is suspected to be incorrect
- After modifying qualification-related workflows
- For periodic review of qualification logic
- As part of audit after `/review-conversation` or `/audit-workflow`

## Execution Flow

### 1. Read Qualification Criteria from Business Context

Extract updated information about all qualification criteria defined in `business-context/`:
- Pricing/budget ranges
- Typical timelines
- Service areas/geography
- Interest level indicators

### 2. List Relevant Workflows

Identify workflows that participate in qualification:
- Main agent workflow (initial collection)
- Specific qualification tools (if they exist)
- Database storage workflows

Use n8n-MCP to list and obtain workflows.

### 3. Analysis by Criterion

For each criterion defined in business-context/:

**Validate three aspects:**

#### A. Question Asked
- Does the agent ask the right question?
- Is it clear?
- Does it offer reference ranges or examples?

#### B. Validation Logic
- Is the response validated against business rules?
- Are out-of-range values identified?
- Are appropriate suggestions made?

#### C. Data Storage
- Is data saved correctly to database?
- Correct format?
- Correct field in the table?
- Error handling if DB fails?

**Search in workflows:**
- Nodes mentioning the criterion keywords
- Prompts asking about it
- Validation and comparison logic

### 4. Generate Validation Checklist

Create file: `/docs/validation/lead-scoring-${DATE}.md`

For each criterion:

| Aspect | Status | Details |
|--------|--------|---------|
| Question asked | OK / Partial / Missing | [Observations] |
| Offers reference ranges | OK / Partial / Missing | [Observations] |
| Validates response | OK / Partial / Missing | [Observations] |
| Suggests alternatives | OK / Partial / Missing | [Observations] |
| Stores in DB | OK / Partial / Missing | [Observations] |

**Responsible workflow:** ${WORKFLOW_NAME}
**Relevant node(s):** ${NODES}

### 5. Generate Suggested Modifications

If problems found, create specific list of changes:

```markdown
## Suggested Modifications for ${WORKFLOW_NAME}

### Change 1: Add criterion question
**Node:** AI Agent main prompt
**Modification:** Add question about [criterion]

### Change 2: Add validation logic
**Node:** New IF node after collecting data
**Logic:** IF value < MIN or value > MAX...
```

### 6. Present Summary

```
Lead scoring validation completed

**Criteria validated:** N/N

**Summary:**
- Correctly implemented: N criteria
- Partially implemented: N criteria
- Not implemented: N criteria

**Problems found:** N

**Next step:** [Recommendation]

**Report:** /docs/validation/lead-scoring-${DATE}.md
```

## Error Handling
- **Business context incomplete:** Continue with available info, warn user
- **No qualification workflows found:** Ask for workflow names
- **n8n-MCP fails:** Check configuration

## Notes
- This skill does NOT modify workflows, only validates
- ALWAYS generate complete checklist
- Prioritize critical problems (unimplemented criteria)
- Can be run periodically as part of QA
- Useful after modifying any qualification workflow
