# Project Overview

**Personal AI Employee FTEs** is a hackathon and educational project for building autonomous AI agents that function as "Digital Full-Time Equivalents (FTEs)." The project enables users to create local-first, agent-driven automation systems where AI agents (powered by Claude Code and Obsidian) proactively manage personal and business affairs 24/7.

## Core Architecture

The architecture follows a **Perception → Reasoning → Action** pattern:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception (Watchers)** | Python Sentinel Scripts | Monitor Gmail, WhatsApp, filesystems, banking APIs |
| **Reasoning (Brain)** | Claude Code | Multi-step reasoning, planning, decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, long-term memory, knowledge base |
| **Action (Hands)** | MCP Servers | External system integration (email, browser, payments) |

## Key Concepts

- **Digital FTE**: An AI agent priced and managed like a human employee, working 168 hours/week at 85-90% cost reduction
- **Watcher Pattern**: Lightweight Python scripts that monitor inputs and create actionable `.md` files in `/Needs_Action`
- **Ralph Wiggum Loop**: A persistence pattern using Stop hooks to keep Claude iterating until tasks complete
- **Human-in-the-Loop (HITL)**: Approval workflow where sensitive actions require manual file movement to `/Approved`
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue reports and proactive suggestions

---

# Project Structure

```
ZA-Personal-AI-Employee-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies registry
├── .qwen/skills/             # Qwen skill integrations
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Browser automation skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool schemas
│       └── scripts/
│           ├── mcp-client.py  # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh
│           ├── stop-server.sh
│           └── verify.py
└── .gitattributes
```

---

# Building and Running

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

## Quick Start

### 1. Initialize Obsidian Vault

Create a vault with the following folder structure:
```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── In_Progress/
├── Pending_Approval/
├── Approved/
├── Done/
├── Accounting/
├── Plans/
└── Briefings/
```

### 2. Start Playwright MCP Server

```bash
# Start the browser automation server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify it's running
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### 3. Configure MCP Servers

Add to `~/.config/claude-code/mcp.json`:
```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": { "HEADLESS": "true" }
    }
  ]
}
```

### 4. Run a Watcher Script

Example: Gmail Watcher (create `gmail_watcher.py`):
```python
# Implement BaseWatcher pattern from the hackathon doc
# Saves new emails as .md files in /Needs_Action
```

### 5. Trigger Claude Code

```bash
# Process pending actions
claude "Check /Needs_Action folder and create Plan.md for each item"
```

---

# Development Conventions

## File Naming

| Location | Pattern | Example |
|----------|---------|---------|
| `/Needs_Action/` | `TYPE_Description.md` | `EMAIL_ClientInquiry.md` |
| `/Pending_Approval/` | `APPROVAL_Action_Description_Date.md` | `APPROVAL_Payment_ClientA_2026-01-07.md` |
| `/Plans/` | `Plan_Description.md` | `Plan_Q1TaxPrep.md` |
| `/Briefings/` | `YYYY-MM-DD_Day_Briefing.md` | `2026-01-06_Monday_Briefing.md` |

## Markdown Frontmatter

All action files use YAML frontmatter:
```yaml
---
type: email
from: client@example.com
subject: Invoice Request
priority: high
status: pending
---
```

## Watcher Script Pattern

All watchers inherit from `BaseWatcher`:
```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseWatcher(ABC):
    @abstractmethod
    def check_for_updates(self) -> list:
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass
    
    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(check_interval)
```

## Human-in-the-Loop Workflow

1. Claude detects sensitive action → writes to `/Pending_Approval/`
2. User reviews and moves file to `/Approved/` or `/Rejected/`
3. Orchestrator triggers MCP action for approved items
4. Result logged, file moved to `/Done/`

---

# Available Skills

## browsing-with-playwright

Browser automation via Playwright MCP for web scraping, form submission, and UI testing.

**Key Commands:**
```bash
# Start server
bash scripts/start-server.sh

# Call tools via MCP client
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Stop server
bash scripts/stop-server.sh
```

**Available Tools:** 22 tools including `browser_navigate`, `browser_click`, `browser_type`, `browser_snapshot`, `browser_take_screenshot`, `browser_evaluate`, `browser_run_code`.

---

# Testing Practices

1. **Watcher Testing**: Run each watcher in isolation, verify `.md` file creation
2. **MCP Verification**: Use `verify.py` before browser-dependent tasks
3. **Approval Flow**: Test HITL with mock payment scenarios
4. **Ralph Loop**: Verify task completion detection and iteration limits

---

# Contribution Guidelines

1. All AI functionality must be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
2. Document new watchers using the `BaseWatcher` template pattern
3. Keep data local-first; secrets never sync (`.env`, tokens, sessions)
4. Follow the tiered achievement model (Bronze → Silver → Gold → Platinum)

---

# References

- [Ralph Wiggum Stop Hook](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Server Protocol](https://modelcontextprotocol.io/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
