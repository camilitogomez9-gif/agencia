---
name: generate-case-report
description: Use when generating an executive report for client review, including problem, analysis, applied fix and validation results.
argument-hint: [case-id]
user-invocable: true
allowed-tools: Read, Write
---

# Skill: Generate Case Report

## Purpose
Generate a complete executive report in Markdown format for client review and approval.

## When to Use
- After `/validate-fix` confirms the fix works
- Before obtaining client approval
- Sixth step in the correction flow

## Execution Flow

### 1. Read All Case Files

Read in order: failed-conversation.json, ideal-conversation.json, problem-description.md, analysis.md, fix-applied.md, validation-result.md, status.md

### 2. Generate Executive Report

**File:** `docs/cases/${CASE_ID}/executive-report.md`

Structure:

1. **Summary** - Problem, solution, validation result, recommendation
2. **Original Problem** - Failed conversation excerpts, what failed, impact
3. **Expected Solution** - Ideal conversation, why it's better
4. **Analysis Performed** - Root cause, responsible workflow, change type
5. **Changes Applied** - Modified node, change description (technical + simple)
6. **Solution Validation** - Testing results table, resulting conversation, comparison
7. **Change Impact** - Affected conversations %, benefits, risks, mitigation
8. **Side-by-Side Comparison** - Failed vs Ideal vs Actual table
9. **Recommendation** - Approval checklist, decision with justification
10. **Next Steps** - If approved (deploy flow) / If rejected (re-analyze flow)
11. **Reference Files** - Links to all case documentation

### 3. Update Case Status

### 4. Present Summary to User

```
Executive report generated for case ${CASE_ID}

**File:** docs/cases/${CASE_ID}/executive-report.md

**Next step:**
1. Share report with client for review
2. Client approves by creating: docs/cases/${CASE_ID}/approved.txt
3. Run: /deploy-to-production ${WORKFLOW_NAME} --case ${CASE_ID}
```

## Error Handling

### If critical files missing:
Generate with available info but mark as incomplete.

### If validation was FAILED:
Warn that generating report is not recommended until fix succeeds.

## Notes
- Report must be understandable for non-technical readers
- Include code only as reference (explain in simple language)
- Side-by-side visual comparison is very useful for the client
- Always include clear recommendation (approve / reject / adjust)
- This is the document the client uses to decide whether to deploy
