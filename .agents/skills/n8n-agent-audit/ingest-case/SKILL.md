---
name: ingest-case
description: Use when creating a new case with failed conversations. Use when user says "create case", "ingest case", "new case", "I have these failed conversations", or provides CRM conversation IDs.
argument-hint: [case-id] [--ids 123,456,789]
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Ingest Case

## Purpose
Create a new workflow modification case by obtaining failed conversations from the CRM system.

## Main Flow (RECOMMENDED): CRM Conversation IDs

### Step 1: Get Case ID and Conversation IDs

If user provides arguments:
```
/ingest-case case-002-example --ids 493,759,742
```

If not, ask:
```
To create the case I need:

1. **Case ID** (e.g.: case-002-short-description):

2. **CRM conversation IDs** (comma-separated):
```

### Step 2: Create Case Directory

```bash
mkdir -p docs/cases/${CASE_ID}
```

### Step 3: Fetch Conversations from CRM

For EACH conversation_id, execute:

```bash
curl -s -X POST "{{CRM_SCRAPER_URL}}" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": ${ID}}'
```

**Expected response:** JSON with structure:
```json
{
  "conversation_id": 493,
  "source": "crm",
  "messages": [
    {"sender": "lead", "name": "...", "text": "..."},
    {"sender": "agent", "name": "...", "text": "..."}
  ]
}
```

Save each response in:
```
docs/cases/${CASE_ID}/conversation-${ID}.json
```

### Step 4: Create Problem Description File

Create `docs/cases/${CASE_ID}/problem-description.md`:

```markdown
# ${CASE_ID}

## Analyzed Conversations
- conversation-${ID1}.json
- conversation-${ID2}.json
...

## Identified Problem
[To be completed after analysis]

## Common Pattern
[To be completed after analysis]

## Suspected Workflow
- [ ] main agent (system prompt)
- [ ] tool workflow
- [ ] other: ___
```

### Step 5: Create Initial Status

Create `docs/cases/${CASE_ID}/status.md`:

```markdown
# Case Status

**Case ID:** ${CASE_ID}
**Created:** ${CURRENT_DATE}
**Status:** INGESTED

## Progress

- [x] Conversations scraped (N/N)
- [ ] Problem documented
- [ ] Root cause analysis
- [ ] Identify workflow/node to modify
- [ ] Draft changes
- [ ] Approve proposed changes
- [ ] Apply fix in SANDBOX
- [ ] Validate fix
- [ ] Client approval
- [ ] Deploy to production

## Case Files

[List of created files]

## Next Step

Analyze conversations and document the common problem.
```

### Step 6: Confirm to User

```
Case ${CASE_ID} created

**Conversations obtained:**
- conversation-493.json
- conversation-759.json
...

**Location:** docs/cases/${CASE_ID}/

**Next step:** Analyze conversations and document the problem in problem-description.md
```

---

## Alternative Flow: Local Files

If user already has local JSON files:

```
/ingest-case case-003 --files /path/to/conv1.json,/path/to/conv2.json
```

1. Copy files to case directory
2. Rename to `conversation-N.json`
3. Create status.md and problem-description.md

---

## CRM Integration

**Scraper Endpoint:**
```
{{CRM_SCRAPER_URL}}
```

**Payload:**
```json
{"conversation_id": 493}
```

**Response:** JSON with conversation messages

---

## Error Handling

### If scraper fails:
```
Warning: Error fetching conversation ${ID}: [error message]

Options:
1. Retry
2. Skip this conversation
3. Provide file manually
```

### If Case ID already exists:
```
Warning: Case ${CASE_ID} already exists.

Options:
1. Use another ID
2. Add conversations to existing case
```

---

## Notes

- The CRM scraper returns conversations in standardized format
- Each conversation is saved as an individual file for easy reference
- Ideal conversation is NOT required at this stage - it's defined during analysis
- The status.md uses consistent format across all cases
