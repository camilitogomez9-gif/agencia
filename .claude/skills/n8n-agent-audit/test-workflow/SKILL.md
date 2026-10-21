---
name: test-workflow
description: Use when creating a test version of a workflow, validating changes without affecting production, A/B testing.
argument-hint: [workflow-name]
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Test Workflow

## Purpose
Create a test version of a modified workflow to validate changes without affecting production.

## When to Use
- After `/modify-workflow` modified a workflow
- Before `/deploy-workflow` for controlled validation
- For A/B testing different versions

## Execution Flow

### 1. Get Workflow Name

### 2. Get Workflow using n8n-MCP

Verify workflow exists and was recently modified.

### 3. Create Copy with "-TEST" Suffix

Using n8n-MCP:
- Name: `${WORKFLOW_NAME}-TEST`
- Description: `[TEST] ${ORIGINAL_DESCRIPTION} - Test version created ${DATE}`
- Tags: Add "test" tag
- Preserve all original configuration

### 4. Deactivate Test Workflow

**CRITICAL:** Deactivate to prevent accidental executions.

### 5. Configure Test Environment (if applicable)

```
NOTE: If the workflow uses external integrations, consider configuring
test environment variables to avoid affecting production:
- CRM_ACCOUNT_ID -> CRM_TEST_ACCOUNT_ID
- DB_URL -> DB_TEST_URL
- Other API endpoints
```

### 6. Guide User for Testing

Generate testing guide with 3 case types:

#### Case 1: Original Problem Case
**Objective:** Verify the reported problem is resolved.
- Execute workflow manually in n8n
- Provide input data from the original error
- Verify expected output

#### Case 2: Happy Path
**Objective:** Verify existing functionality still works.
- Test with typical valid inputs
- Verify agent responses are correct
- Verify data is saved to DB
- Verify integrations work

#### Case 3: Edge Cases
**Objective:** Verify robustness.
- Test with boundary values
- Test with invalid/unexpected input
- Verify graceful error handling

### Validation Checklist

- [ ] Original problem resolved
- [ ] Normal cases work correctly
- [ ] Edge cases handled appropriately
- [ ] Agent tone and voice appropriate
- [ ] Data saved correctly in DB
- [ ] Integrations working
- [ ] No visible errors to lead
- [ ] Acceptable performance

### 7. Document Testing

Create file: `/docs/tests/test-${WORKFLOW_NAME}-${DATE}.md`

Result states:
- **APPROVED:** Ready for production
- **APPROVED WITH OBSERVATIONS:** Works but minor improvements needed
- **REJECTED:** Requires corrections before deploying

### 8. Offer Interactive Testing (Optional)

Help with additional test cases, synthetic data, log analysis, or comparison with original.

### 9. Cleanup Post-Testing

Options:
1. Keep test workflow for future reference
2. Delete test workflow (already validated)
3. Archive (deactivated but available)

### 10. Present Summary

```
Workflow testing completed

**Workflow:** ${WORKFLOW_NAME}
**Test version:** ${WORKFLOW_NAME}-TEST
**Status:** ${STATUS} (Approved / Rejected)

**Cases tested:** ${TOTAL}
- Successful: N
- Failed: N

**Next step:**
[If approved: /changelog-workflow + /deploy-workflow]
[If rejected: /modify-workflow + re-test]
```

## Testing Types Supported

1. **Manual Testing** - User executes manually in n8n
2. **Real Conversation Testing** - Use data from previous failed conversations
3. **Regression Testing** - Verify changes don't break existing functionality
4. **A/B Testing** - Compare original vs modified with same inputs

## Notes
- ALWAYS create test version, NEVER test directly in production
- ALWAYS deactivate test workflow
- Test minimum 3 case types
- Document ALL results
- If tests fail, go back to `/modify-workflow`, do NOT deploy
- Keep test workflow until after successful deployment
