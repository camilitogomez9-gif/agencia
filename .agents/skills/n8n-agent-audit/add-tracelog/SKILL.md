---
name: add-tracelog
description: Creates a new entry in the project's tracelog system for immutable event logging.
user-invocable: true
allowed-tools: Read, Write
---

# Skill: add-tracelog

This skill allows recording an important project event immutably in the tracelog system (`docs/tracelog/`).

## Usage

The user will provide event context and type (optional, Codex can infer). Allowed types:
- `MEETING`: Video calls or synchronous meetings.
- `CHAT`: Critical agreements or decisions via messaging/email.
- `CASE`: Resolutions and deployments originating from the case system.
- `SYS-UPDATE`: Updates to infrastructure, global prompts, or base documentation.

## Process

1. **Analyze input:** Extract date (use current if not provided), event type, participants, relevant tags, related cases (related_cases) and related logs (related_logs) if applicable.
2. **Generate folder:** Directory name format: `YYYY-MM-DD_[TYPE]_[short_description]`. Example: `docs/tracelog/2026-03-08_MEETING_prompt-changes/`.
3. **Write main content (`tracelog.md`):**
    - Include Frontmatter (date, type, participants, tags, related_cases, related_logs).
    - Structure body with: "Summary", "Attached Evidence" (list files if provided), and "Next Steps".
4. **Save files:**
    - Save content to `docs/tracelog/[FOLDER_NAME]/tracelog.md`.
    - If user provided transcriptions or text evidence, save as `transcription.txt` in same folder.
5. **Confirm:** Inform user the log directory has been created successfully.
