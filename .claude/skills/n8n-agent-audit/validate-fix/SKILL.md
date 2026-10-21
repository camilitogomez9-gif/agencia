---
name: validate-fix
description: Use when validating that the applied fix produces the ideal conversation. Executes modified workflow and compares result.
argument-hint: [case-id]
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Validate Fix

## Purpose
Validate that workflow modifications produce the ideal conversation. Execute the modified workflow with inputs from the failed conversation and compare results with the ideal conversation.

## When to Use
- After `/modify-workflow` has applied changes
- Before `/deploy-to-production` to ensure the fix works
- Fourth step in the correction flow

## Execution Flow

### 1. Validate Prerequisites

```bash
if [ ! -d "docs/cases/${CASE_ID}" ]; then
  echo "Error: Case ${CASE_ID} not found"
  exit 1
fi

if [ ! -f "docs/cases/${CASE_ID}/analysis.md" ]; then
  echo "Warning: analysis.md not found. Run /analyze-case ${CASE_ID} first"
fi

if [ ! -f "docs/cases/${CASE_ID}/fix-applied.md" ]; then
  echo "Warning: fix-applied.md not found. Changes may not have been applied."
fi
```

### 2. Read Case Files

- Failed conversation (testing input - extract lead messages)
- Ideal conversation (expected reference)
- Analysis (which workflow was modified)

### 3. Prepare Testing Inputs

Extract ONLY lead messages from the failed conversation.

### 4. Execute Workflow with Testing Inputs

#### Option A: Conversation Replayer Workflow (Infrastructure)

```bash
curl -X POST "{{N8N_API_BASE_URL}}/api/v1/workflows/${REPLAYER_ID}/execute" \
  -H "X-N8N-API-KEY: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"target_workflow": "{{MAIN_AGENT_WORKFLOW_ID}}", "lead_messages": [...]}'
```

#### Option B: Manual Calls to Main Agent

```bash
curl -X POST "{{SANDBOX_WEBHOOK_URL}}" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test-${CASE_ID}", "input": "${message_text}"}'
```

**IMPORTANT:** Use unique session ID, send sequentially, wait for responses.

### 5. Compare Result with Ideal Conversation

#### A. Compare Agent Messages

| # | Lead Input | Ideal | Actual | Status |
|---|------------|-------|--------|--------|

#### B. Compare Agent Final State

| Variable | Ideal | Actual | Status |
|----------|-------|--------|--------|

#### C. Compare Tools Executed

### 6. Determine Validation Result

#### A. Fix SUCCESSFUL
All responses match, state matches, correct tools executed.
**Next:** `/generate-case-report ${CASE_ID}`

#### B. Fix PARTIAL
Some match, others similar. State mostly correct.
**Options:** Accept differences or adjust workflow.

#### C. Fix FAILED
Responses very different, incorrect state, wrong tools.
**Next:** Re-analyze and re-modify.

### 7. Generate validation-result.md

Save to: `docs/cases/${CASE_ID}/validation-result.md`

### 8. Update Case Status

### 9. Present Summary to User

## Validation Metrics

**SUCCESSFUL if:**
- Identical messages: >= 80%
- Correct agent state: 100%
- Correct tools executed: 100%

**PARTIAL if:**
- Identical messages: 50-79%
- Correct agent state: >= 80%
- Correct tools executed: >= 80%

**FAILED if:**
- Identical messages: < 50%
- Correct agent state: < 80%
- Correct tools executed: < 80%

## Notes
- CRITICAL validation before deploying to production
- If validation fails, do NOT continue with report or deployment
- Minor wording differences acceptable if logic is correct
- Agent state and tools are more important than exact text
- Always capture execution ID for debugging
