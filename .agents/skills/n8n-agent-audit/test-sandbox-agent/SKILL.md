---
name: test-sandbox-agent
description: Use to test the main SANDBOX agent after applying changes. Use when user says "test agent", "test sandbox", "simulate conversation", "validate fix".
argument-hint: [sessionId] [initial message]
user-invocable: true
allowed-tools: Bash, Read, Write
---

# Skill: Test Sandbox Agent

## Purpose
Test the main SANDBOX agent by sending messages and analyzing responses to validate that applied changes work correctly.

## Endpoint and Configuration

**Endpoint:**
```
{{SANDBOX_WEBHOOK_URL}}
```

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Payload (REQUIRED):**
```json
{
  "input": "lead message",
  "sessionId": "unique-conversation-identifier"
}
```

**Response:**
```json
{
  "output": "agent response"
}
```

---

## Test Flow

### Step 1: Generate Unique Session ID

Each test conversation needs a unique sessionId for agent memory to work correctly.

Suggested format: `test-{case-id}-{timestamp}`

### Step 2: Send Initial Message

```bash
curl -s -X POST "{{SANDBOX_WEBHOOK_URL}}" \
  -H "Content-Type: application/json" \
  -d '{"input": "LEAD_MESSAGE", "sessionId": "SESSION_ID"}'
```

### Step 3: Analyze Response

Verify:
- Agent follows the correct conversation path
- Asks expected questions
- Does NOT do things it shouldn't (per the case)

### Step 4: Continue Conversation

Send multiple messages with the SAME sessionId:

```bash
curl -s -X POST "{{SANDBOX_WEBHOOK_URL}}" \
  -H "Content-Type: application/json" \
  -d '{"input": "lead response", "sessionId": "SAME_SESSION_ID"}'
```

### Step 5: Document Results

Save to: `docs/cases/${CASE_ID}/test-results-${TIMESTAMP}.md`

```markdown
# Test Results - ${CASE_ID}

**Date:** ${DATE}
**Session ID:** ${SESSION_ID}

## Conversation

**Lead:** message 1
**Agent:** response 1

**Lead:** message 2
**Agent:** response 2

## Criteria Evaluated

| Criterion | Expected | Result |
|-----------|----------|--------|
| Asks X | YES | Pass/Fail |
| Does NOT do Y | NO | Pass/Fail |

## Verdict
PASS / FAIL

## Notes
[Additional observations]
```

---

## Simulate Existing Case Conversation

1. Read original conversation from case files
2. Extract lead messages only
3. Send sequentially to SANDBOX with same sessionId
4. Compare original (failed) responses vs new (corrected) responses

---

## Important Notes

- **Unique sessionId:** Each test conversation must have a different sessionId
- **Persistent memory:** Agent remembers previous messages for same sessionId
- **No message limit:** Send as many messages as needed
- **Synchronous response:** Endpoint responds immediately
- **Valid JSON:** Ensure quotes are properly escaped in payload

## Troubleshooting

### Empty response
- Verify payload has both `input` AND `sessionId`
- Verify JSON is valid

### Connection error
- Verify SANDBOX workflow is active in n8n
- Check workflow ID: `{{MAIN_AGENT_WORKFLOW_ID}}`

### Unexpected response
- Verify system prompt changes were applied correctly
- Try with a new sessionId (clean memory)
