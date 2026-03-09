---
name: scheduler
description: Schedule recurring tasks via cron or Task Scheduler
---

# Scheduler

## Schedules

### Daily Briefing (8 AM)

**Windows Task Scheduler:**
- Trigger: Daily at 8:00 AM
- Action: `python orchestrator.py AI_Employee_Vault`

**Cron:**
```
0 8 * * * python orchestrator.py AI_Employee_Vault
```

### Weekly Audit (Sunday 8 PM)

**Cron:**
```
0 20 * * 0 python orchestrator.py --weekly-audit
```
