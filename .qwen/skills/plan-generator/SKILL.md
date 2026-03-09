---
name: plan-generator
description: Generate structured Plan.md files from action items
---

# Plan Generator

## Plan Format

```markdown
---
type: plan
status: in_progress
created: 2026-03-05T16:00:00
---

# Plan: Respond to Client Email

## Objective
Generate and send response within 24 hours.

## Steps
- [x] Read email
- [ ] Draft response
- [ ] Get approval
- [ ] Send email
```

## Usage

Qwen Code creates Plan.md files in `Plans/` folder with:
- Clear objectives
- Step-by-step tasks
- Approval requirements
- Progress tracking
