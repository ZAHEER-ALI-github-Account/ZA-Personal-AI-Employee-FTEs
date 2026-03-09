---
name: hitl-approval-workflow
description: Human-in-the-Loop approval workflow for sensitive actions
---

# HITL Approval Workflow

## Workflow

1. AI creates approval request in `Pending_Approval/`
2. Human reviews and moves to `Approved/` or `Rejected/`
3. Orchestrator executes approved actions
4. Result logged to `Done/`

## Folders

- `Pending_Approval/` - Awaiting review
- `Approved/` - Ready to execute
- `Rejected/` - Declined actions

## Approval Thresholds

| Action | Auto | Requires Approval |
|--------|------|-------------------|
| Email to known contact | Yes | No |
| Email to new contact | No | Yes |
| Payment | Never | Always |
| LinkedIn post | No | Always |
