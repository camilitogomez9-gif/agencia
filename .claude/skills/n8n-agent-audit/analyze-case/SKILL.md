---
name: analyze-case
description: Use when analyzing a case comparing failed vs ideal conversation, identifying root cause and determining necessary changes.
argument-hint: [case-id]
user-invocable: true
allowed-tools: Read, Write, Grep, Glob
---

# Skill: Analyze Case

## Purpose
Perform complete comparative analysis between failed and ideal conversation, identify root cause, determine responsible workflow(s) and suggest necessary changes.

## When to Use
- After `/ingest-case` has created the case
- Before `/modify-workflow` to know what to change
- Second step in the correction flow

## Execution Flow

### 1. Validate Case Exists

```bash
if [ ! -d "docs/cases/${CASE_ID}" ]; then
  echo "Error: Case ${CASE_ID} not found"
  echo "Verify Case ID or run first: /ingest-case ${CASE_ID}"
  exit 1
fi
```

### 2. Read Case Files

#### A. Read Failed Conversation
```
Read: docs/cases/${CASE_ID}/failed-conversation.json
```

**Extract:**
- Metadata (case_id, date, lead_name, issue_type)
- Complete messages (timestamp, sender, text)
- Agent state (all state variables)

#### B. Read Ideal Conversation
```
Read: docs/cases/${CASE_ID}/ideal-conversation.json
```

#### C. Read Problem Description
```
Read: docs/cases/${CASE_ID}/problem-description.md
```

**Extract:**
- Problem identified by user
- Suspected workflow
- Expected modification type

### 3. Automatic Conversation Comparison

#### A. Compare Messages

For each pair of messages (same index), detect differences:

```markdown
### Message ${INDEX} - ${SENDER}

**Input (Lead):**
"${LEAD_MESSAGE}"

**Failed Response (Agent):**
"${FAILED_AGENT_RESPONSE}"

**Ideal Response (Agent):**
"${IDEAL_AGENT_RESPONSE}"

**Analysis:**
[Explain what's wrong in the failed response]
[Explain why ideal is correct]

**Key differences:**
- [Difference 1]
- [Difference 2]
```

#### B. Compare Agent State

```markdown
## Agent State Comparison

| Variable | Failed | Ideal | Analysis |
|----------|--------|-------|----------|
| criterion_validated | false | true | Not validated |
| lead_qualified | true | false | Incorrectly qualified |
```

#### C. Compare Tools Executed

```markdown
## Tools Executed

### Failed
- think (1x)
- tool_1 (1x)
- tool_2 NOT executed

### Ideal
- think (1x)
- tool_1 (1x)
- tool_2 executed successfully
```

### 4. Root Cause Identification

Based on:
1. Message differences
2. Agent state differences
3. Tool execution differences
4. User's problem description

```markdown
## Root Cause Identified

### Main Problem
[Specific problem description]

### Observed Symptoms
1. [Symptom 1]
2. [Symptom 2]

### Expected Behavior
[What should happen]
```

### 5. Identify Responsible Workflow(s)

```markdown
## Responsible Workflow(s)

### Primary: ${TOOL_NAME} (SANDBOX)
- **ID:** ${TOOL_ID}
- **Nodes:** N
- **Reason:** This tool should validate X but is not doing it correctly

### Secondary: main agent (SANDBOX)
- **ID:** {{MAIN_AGENT_WORKFLOW_ID}}
- **Reason:** Prompt could improve to explicitly mention X
```

### 6. Fetch Workflow(s) Using n8n-MCP

For each identified workflow, use n8n-MCP to get complete structure.

**Analyze:**
- Current node configuration
- Implemented logic
- n8n expressions used
- Current prompts (if AI Agent)

### 7. Determine Necessary Changes

Include specific code or configuration changes with before/after examples.

### 8. Generate Priority and Impact Estimation

### 9. Generate analysis.md File

Save to: `docs/cases/${CASE_ID}/analysis.md`

### 10. Update Case Status

### 11. Present Summary to User

```
Analysis of case ${CASE_ID} completed

**Problem identified:** [Brief description]
**Root cause:** [Specific cause]
**Workflow(s) to modify:** [List]
**Priority:** High / Medium / Low

**Next step:**
/modify-workflow ${WORKFLOW_NAME} --case ${CASE_ID}
```

## Error Handling

- If case doesn't exist: suggest `/ingest-case` first
- If files missing: list them and ask user to complete
- If JSON invalid: report parse error
- If no clear differences: warn and suggest manual review

## Message Comparison Format

For visual clarity, use tabular format:

```markdown
| # | Sender | Failed | Ideal | Status |
|---|--------|--------|-------|--------|
| 1 | lead   | "Hello..." | "Hello..." | Identical |
| 2 | agent  | "Hi!..." | "Hi!..." | Identical |
| 3 | lead   | "My budget is $X" | "My budget is $X" | Identical |
| 4 | agent  | "Perfect, we have..." | "I understand. Our..." | DIFFERENT |
```

## Notes
- This analysis is CRITICAL - determines what to modify
- Always include specific code for proposed changes
- Prioritize changes by impact (primary vs secondary vs optional)
- The analysis.md serves as permanent case documentation
