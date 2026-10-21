---
name: review-conversation
description: Use when analyzing an erroneous conversation from CRM, identifying what failed in the AI agent, determining which workflow needs modification.
argument-hint: [conversation-id]
user-invocable: true
allowed-tools: Bash(curl *), Read, Write
---

# Skill: Review Conversation

## Purpose
Analyze erroneous conversations reported from CRM to identify AI agent failures and determine which n8n workflow needs correction.

## When to Use
- Client reports an erroneous conversation
- Need to understand what failed in the AI agent
- Need to identify the responsible workflow
- Before running `/audit-workflow` for context

## Execution Flow

### 1. Get Conversation ID

### 2. Fetch Conversation from CRM API

```bash
curl -X GET \
  "${CRM_API_URL}/api/v1/accounts/${CRM_ACCOUNT_ID}/conversations/${CONVERSATION_ID}/messages" \
  -H "api_access_token: ${CRM_API_TOKEN}" \
  -H "Content-Type: application/json"
```

### 3. Save Complete Conversation

Save to: `/docs/conversations/conv-${CONVERSATION_ID}-${DATE}.json`

### 4. Analyze Conversation

#### A. Conversation Flow
- Did agent follow expected flow?
- Were there interruptions or logical jumps?
- Was context lost between messages?

#### B. Agent Responses vs Expected
- Were responses appropriate to context?
- Did tone match the configured agent persona?
- Were there comprehension errors?
- Repetitive or contradictory responses?

#### C. Information Collected
Verify agent correctly collected all qualification criteria defined in business-context/:
- Criterion 1 (e.g., Budget/Price range)
- Criterion 2 (e.g., Timeline/Urgency)
- Criterion 3 (e.g., Location/Geography)
- Criterion 4 (e.g., Interest Level/Buying stage)

#### D. Tone and Voice
- Did agent present itself with correct persona?
- Was it professional but approachable?
- Did it correctly describe products/services?
- Did it offer relevant references?

#### E. Technical Errors
- Visible error messages?
- Failed integrations?
- Timeouts or unusual delays?

### 5. Identify Responsible Workflow

- If prompt/response problem → Main Agent workflow
- If specific tool problem → Corresponding modular workflow
- If detection/routing problem → Support nodes

### 6. Generate Analysis Report

Create file: `/docs/conversations/analysis-${CONVERSATION_ID}-${DATE}.md`

Include: executive summary, conversation details, identified problems with severity, qualification criteria analysis, tone assessment, responsible workflow identification, next steps.

### 7. Suggest Next Step

```
Analysis completed

**Responsible workflow:** [Name]
**Main problem:** [Brief description]

**Suggested next step:**
/audit-workflow [workflow-name]

**Files generated:**
- /docs/conversations/conv-${CONVERSATION_ID}-${DATE}.json
- /docs/conversations/analysis-${CONVERSATION_ID}-${DATE}.md
```

## Environment Variables Required
- `CRM_API_URL`
- `CRM_API_TOKEN`
- `CRM_ACCOUNT_ID`

## Error Handling
- **CRM API fails:** Check env vars, offer manual JSON input
- **Conversation not found:** Verify ID
- **No messages:** Suggest different conversation

## Notes
- ALWAYS save original conversation before analyzing
- ALWAYS generate analysis report
- NEVER modify workflows from this skill
- This skill is ANALYSIS ONLY, not correction
- Delegate technical audit to `/audit-workflow`
