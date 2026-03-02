# 🤖 AI Employee FTE - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is a **Bronze Tier** implementation of the Personal AI Employee Hackathon. It provides the foundational layer for an autonomous AI agent that proactively manages your personal and business affairs using **Qwen Code** and Obsidian.

---

## 📋 Bronze Tier Deliverables

✅ **Completed:**

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] `Business_Goals.md` template
- [x] One working Watcher script (File System Watcher)
- [x] Qwen Code integration (via Orchestrator)
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Plans`, `/Pending_Approval`, `/Approved`, `/Accounting`, `/Briefings`
- [x] All Python scripts use only standard library (no external dependencies)

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                     │
│                      (Bronze Tier)                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  External Input │
│  (File Drop)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  File System Watcher (Python)                               │
│  - Monitors Drop_Folder for new files                       │
│  - Creates action files in Needs_Action                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator (Python)                                      │
│  - Reads Needs_Action items                                 │
│  - Generates Qwen Code prompts                              │
│  - Manages folder flow                                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Qwen Code (Reasoning Engine)                               │
│  - Reads action files                                       │
│  - Creates plans                                            │
│  - Flags items for approval                                 │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Obsidian Vault (Memory/GUI)                                │
│  - Dashboard.md                                             │
│  - Company_Handbook.md                                      │
│  - Business_Goals.md                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Qwen Code](https://github.com/anthropics/qwen-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |

### Step 1: Clone/Download

```bash
cd ZA-Personal-AI-Employee-FTEs
```

### Step 2: Install Dependencies

Bronze Tier uses **only Python standard library** - no installation needed!

```bash
# Optional: Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Verify Vault Structure

Ensure the following folders exist:

```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Accounting/
├── Briefings/
├── Invoices/
└── Logs/
```

And these files:

- `Dashboard.md`
- `Company_Handbook.md`
- `Business_Goals.md`

### Step 4: Open Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder

---

## 📖 Usage Guide

### Workflow Overview

1. **Drop a file** into the `Drop_Folder`
2. **File System Watcher** detects it and creates an action file in `Needs_Action`
3. **Orchestrator** generates a Claude Code prompt
4. **Claude Code** processes the item and creates a plan
5. **Human** reviews and approves if needed
6. **Task** moves to `Done`

### Running the File System Watcher

**Option A: Interactive Mode**

```bash
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault
```

**Option B: Using Default Path**

```bash
cd watchers
python filesystem_watcher.py
```

**Option C: Custom Drop Folder**

```bash
python filesystem_watcher.py /path/to/vault /path/to/drop_folder
```

Press `Ctrl+C` to stop the watcher.

### Running the Orchestrator

**One-time Check:**

```bash
python orchestrator.py AI_Employee_Vault
```

**Watch Mode (Continuous Monitoring):**

```bash
python orchestrator.py AI_Employee_Vault --watch --interval 60
```

**With Custom Interval:**

```bash
python orchestrator.py AI_Employee_Vault --watch --interval 30
```

### Processing with Qwen Code

After running the orchestrator, it will generate a prompt. Then:

```bash
cd AI_Employee_Vault
qwen "Process items in Needs_Action folder"
```

Or paste the generated prompt directly into Qwen Code.

---

## 📁 Folder Structure

```
ZA-Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and targets
│   ├── Inbox/                  # Raw incoming items
│   ├── Needs_Action/           # Items requiring AI attention
│   ├── Plans/                  # Active plans and strategies
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Ready for execution
│   ├── Done/                   # Completed items
│   ├── Accounting/             # Financial records
│   ├── Briefings/              # CEO briefings
│   ├── Invoices/               # Generated invoices
│   ├── Logs/                   # System logs
│   └── Drop_Folder/            # Drop files here for processing
├── watchers/
│   ├── base_watcher.py         # Abstract base class
│   └── filesystem_watcher.py   # File system monitor
├── orchestrator.py             # Main orchestration script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔧 Configuration

### Watcher Configuration

Edit `watchers/filesystem_watcher.py` to customize:

```python
# Check interval (seconds)
check_interval = 30

# Drop folder location
drop_folder = Path(vault_path) / 'Drop_Folder'
```

### Orchestrator Configuration

Edit `orchestrator.py` to customize:

```python
# Watch interval (seconds)
interval = 60

# Log location
log_dir = self.folders['logs']
```

---

## 🧪 Testing the Bronze Tier

### Test 1: File Drop

1. Start the File System Watcher:
   ```bash
   python watchers/filesystem_watcher.py AI_Employee_Vault
   ```

2. Drop a test file:
   ```bash
   echo "Test content" > AI_Employee_Vault/Drop_Folder/test_document.txt
   ```

3. Verify action file created:
   ```bash
   ls AI_Employee_Vault/Needs_Action/
   # Should see: FILE_test_document_txt.md
   ```

### Test 2: Orchestrator

1. Run the orchestrator:
   ```bash
   python orchestrator.py AI_Employee_Vault
   ```

2. Verify it generates a Qwen Code prompt

3. Check the logs:
   ```bash
   cat AI_Employee_Vault/Logs/orchestrator_*.log
   ```

### Test 3: Qwen Code Integration

1. Navigate to vault:
   ```bash
   cd AI_Employee_Vault
   ```

2. Run Qwen:
   ```bash
   qwen "Read the Company_Handbook.md and summarize the approval rules"
   ```

3. Verify Qwen can read and write to the vault

---

## 📊 Dashboard

The `Dashboard.md` provides real-time status:

| Section | Description |
|---------|-------------|
| Executive Summary | Pending actions, in progress, approvals |
| Today's Priorities | High-priority tasks for today |
| Recent Activity | Last 5 completed tasks |
| Pending Approval | Items awaiting human decision |
| Business Metrics | Revenue tracking, active projects |
| System Status | Watcher and orchestrator status |

---

## 🔐 Security Notes

### Bronze Tier Security

- ✅ No credentials stored in vault
- ✅ All data local-first
- ✅ Audit logging enabled
- ✅ Human-in-the-loop for sensitive actions

### Best Practices

1. **Never commit** `.env` files or credentials
2. **Review logs** regularly in `AI_Employee_Vault/Logs/`
3. **Test in dry-run** mode before automating actions
4. **Start with low stakes** tasks to build confidence

---

## 📈 Upgrading to Silver Tier

To upgrade to Silver Tier, add:

1. **Gmail Watcher** - Monitor Gmail for new emails
2. **WhatsApp Watcher** - Monitor WhatsApp Web (requires Playwright)
3. **MCP Server** - Send emails via Gmail API
4. **Approval Workflow** - Full HITL implementation
5. **Scheduling** - Cron/Task Scheduler integration

---

## 🐛 Troubleshooting

### Watcher Not Detecting Files

- Ensure the drop folder path is correct
- Check file permissions
- Verify the watcher is running (check logs)

### Orchestrator Not Finding Items

- Ensure files have `.md` extension
- Check the `Needs_Action` folder path
- Review orchestrator logs

### Qwen Code Not Processing

- Verify Qwen Code is installed: `qwen --version`
- Ensure you're in the vault directory
- Check that files are readable

---

## 📚 Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/anthropics/qwen-code)
- [Obsidian Documentation](https://help.obsidian.md/)
- [Python Standard Library](https://docs.python.org/3/library/)

---

## 🎯 Next Steps

1. **Test the watcher** with a sample file drop
2. **Run the orchestrator** to generate a Qwen prompt
3. **Process with Qwen Code** to complete a full cycle
4. **Customize the handbook** with your own rules
5. **Upgrade to Silver Tier** by adding Gmail/WhatsApp watchers

---

## 📝 License

This project is part of the Personal AI Employee Hackathon. Feel free to use, modify, and share.

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
