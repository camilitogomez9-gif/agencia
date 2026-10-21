---
name: changelog-workflow
description: Use when recording changes to a workflow, maintaining modification history, documenting change reasons.
argument-hint: [workflow-name] --case [case-id]
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Skill: Changelog Workflow

## Purpose
Record and document all changes made to n8n workflows, maintaining complete history with diffs, reasons, and context.

## When to Use
- **WITH case:** After `/modify-workflow` with --case (MAIN FLOW)
- After `/modify-workflow` modified a workflow
- Before `/deploy-to-production` to document what will be deployed
- For change auditing
- To maintain workflow evolution history

## Case Integration

### With `--case [case-id]`:
Automatically extracts information from case files:
- Description from `analysis.md`
- Reason from `problem-description.md`
- Technical details from `fix-applied.md`
- Reference to complete case

**Does NOT ask user for info** - everything comes from the case.

### Without `--case`:
Manual/legacy mode:
- Asks user for description, reason, type
- Generates diff manually
- No case reference

## Execution Flow

### 1. Get Workflow Name

### 2. Detect Modified Workflow

Find most recent backup in `/workflows/archive/`:

```bash
ls -t /workflows/archive/${WORKFLOW_NAME}-*.json | head -1
```

If no backup: ask if this is a new workflow or suggest creating backup first.

### 3. Get Current Workflow Version via n8n-MCP

### 4. Generate Diff Between Versions

Compare backup with current:
- Nodes added
- Nodes deleted
- Nodes modified (which fields changed)
- Connections changed

### 5. Get Change Information

#### With --case: Read automatically from case files
#### Without --case: Ask user for:
1. Description of the change
2. Reason for the change
3. Related CRM conversation ID (optional)
4. Change type (bug fix, new feature, prompt improvement, optimization, refactoring)

### 6. Update or Create CHANGELOG

File: `/docs/workflows/CHANGELOG-${WORKFLOW_NAME}.md`

New entries go at the top (most recent first).

```markdown
# Changelog: ${WORKFLOW_NAME}

## [${DATE}] - ${CHANGE_TYPE}

### Modified by
[User or "Claude Code"]

### Description
${DESCRIPTION}

### Reason
${REASON}

### Related Case
- **Case ID:** ${CASE_ID} (if applicable)
- **Analysis:** docs/cases/${CASE_ID}/analysis.md

### Technical Changes

#### Nodes Added
- **[Node Name]** (${TYPE}): [Purpose]

#### Nodes Deleted
- **[Node Name]** (${TYPE}): [Why removed]

#### Nodes Modified
##### [Node Name]
**Changes:**
- `${FIELD}`: `"${BEFORE}"` -> `"${AFTER}"`
**Impact:** [Effect on agent behavior]

#### Connections Modified
[If flow changed]

### Detailed Diff

<details>
<summary>View complete diff (JSON)</summary>

```diff
[Diff in diff format]
```

</details>

### Testing
- **Test performed:** Yes / No
- **Result:** [If tested]
- **Documentation:** `/docs/tests/test-${WORKFLOW_NAME}-${DATE}.md`

### Deployment
- **Deployed to production:** Yes / Pending / No
- **Deploy date:** ${DEPLOY_DATE}

### Related Files
- **Pre-change backup:** `/workflows/archive/${WORKFLOW_NAME}-${TIMESTAMP}.json`
```

### 7. Optional: Create Git Commit

If project is a git repo, offer to commit the changelog.

### 8-9. Summary and Versioning Suggestions

Suggest semantic versioning based on change type:
- Bug fix -> Patch
- New feature -> Minor
- Breaking change -> Major

## Change Types

1. **Bug fix** - Logic error, failed integration, incorrect expression
2. **Prompt improvement** - Add instructions, improve tone, include examples
3. **New feature** - New criterion, new API, new validation
4. **Optimization** - Reduce redundancy, improve performance
5. **Refactoring** - Reorganize, rename for clarity, modularize

## Notes
- ALWAYS run after `/modify-workflow` and before deployment
- Keeping changelog updated facilitates auditing and debugging
- Auto-diff may not capture subtle semantic changes
- User description is critical for understanding the "why"
- Relating to CRM conversation helps trace change origins
- Changelog is living documentation of the workflow
