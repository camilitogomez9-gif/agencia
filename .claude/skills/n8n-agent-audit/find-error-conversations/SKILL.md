---
name: find-error-conversations
description: Use when searching for conversations with errors, finding error cases in CRM, identifying conversations where the agent failed, or reviewing conversations with specific problems.
argument-hint: "[error description] [--id conversation-id] [--from date] [--to date] [--limit number]"
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Write, Bash
---

## What This Skill Does

Searches CRM conversations containing a specific error, allowing identification of cases for AI agent correction. Can search in bulk (last N conversations) or analyze a specific conversation by ID.

## Use Cases

- Client reports repeated error: "find conversations where the agent didn't validate the budget"
- Specific conversation analysis: "analyze conversation ID 12345 for the overly formal tone error"
- Temporal search: "find conversations from last month where agent didn't qualify correctly"

## Arguments

- **Error description** (required) - Natural text describing the error to search for
- **`--id [conversation-id]`** (optional) - Specific CRM conversation ID
- **`--from [date]`** and **`--to [date]`** (optional) - Date range (YYYY-MM-DD format)
- **`--limit [number]`** (optional) - Maximum conversations to review (default: 20)

## Step-by-Step Process

### Step 1: Validate Environment Variables

Verify CRM_API_URL, CRM_API_TOKEN, CRM_ACCOUNT_ID are configured.

### Step 2: Parse Arguments

Extract error description, --id, --from, --to, --limit from arguments.

### Step 3: Call n8n Workflow

Use n8n-MCP to execute the "Find Error Conversations" workflow:

```json
{
  "error_description": "[description]",
  "conversation_id": "[ID or null]",
  "date_from": "[date or null]",
  "date_to": "[date or null]",
  "limit": 20
}
```

### Step 4: Process Results

Expected response structure:
```json
{
  "total_reviewed": 20,
  "errors_found": 3,
  "conversations": [
    {
      "id": "12345",
      "date": "2026-03-05T10:30:00Z",
      "lead_name": "Lead Name",
      "error_snippet": "The agent qualified the lead without validating..."
    }
  ]
}
```

### Step 5: Format Output

**If errors found:**
```markdown
# Conversations with Errors Found

**Error searched:** [description]
**Conversations reviewed:** [total_reviewed]
**Conversations with error:** [errors_found]

---

## Conversation #1
- **ID:** [id] (to ingest: `/ingest-case --ids [id]`)
- **Date:** [formatted date]
- **Lead:** [lead_name]
- **Error detected:**
  > [error_snippet]

---

## Next Steps

1. Review conversations in CRM
2. To ingest as case: `/ingest-case --ids [id]`
3. To search more: `/find-error-conversations "same error" --limit 50`
```

**If no errors found:**
Suggest refining search: wider date range, increased limit, reformulated description, or known conversation ID.

### Step 6: Documentation (Optional)

If requested, save search log to `docs/error-searches/[date]-[short-description].md`

## Important Notes

### Cost Management
- **Default limit:** 20 conversations to control token usage
- ~500-1000 tokens per conversation reviewed
- Suggest increasing gradually: 20 -> 50 -> 100

### Protections
- Read-only - does not modify CRM conversations
- Does not execute actions on found conversations
- Requires confirmation before ingesting as case
- Validates environment variables before executing

### Edge Cases
- **No CRM connection:** Report API error, check credentials
- **Invalid ID:** Report conversation doesn't exist
- **Invalid dates:** Correct format or reject
- **Excessive limit (>100):** Warn about token cost and execution time
- **Vague description:** Suggest being more specific

### Integration with Case Workflow
Once an error conversation is identified:
1. User reviews in CRM manually
2. User decides if it's a valid correction case
3. User ingests with: `/ingest-case --ids [id]`
4. Case follows normal flow: analyze -> fix -> validate

### Dependencies
- n8n workflow "Find Error Conversations" must exist and be active
- CRM API access (read-only)
- n8n-MCP configured and working

## Examples

```
/find-error-conversations "agent didn't validate budget before qualifying lead"
/find-error-conversations "overly formal tone" --from 2026-03-01 --to 2026-03-05
/find-error-conversations "agent didn't ask about location" --id 12345
/find-error-conversations "agent didn't use tools correctly" --limit 50
```
