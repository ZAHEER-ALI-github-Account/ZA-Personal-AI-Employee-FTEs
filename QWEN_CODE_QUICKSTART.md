# 🚀 Quick Start with Qwen Code

## Commands You Need

### 1. Start the File Watcher

```bash
cd C:\Users\user\Documents\GitHub\ZA-Personal-AI-Employee-FTEs
python watchers/filesystem_watcher.py AI_Employee_Vault
```

This runs continuously and watches for new files in `Drop_Folder/`.

---

### 2. Drop a File to Process

In a **new terminal**:

```bash
echo "Please review this document" > AI_Employee_Vault/Drop_Folder\my_task.txt
```

The watcher will detect it and create an action file.

---

### 3. Run the Orchestrator

In a **new terminal**:

```bash
cd C:\Users\user\Documents\GitHub\ZA-Personal-AI-Employee-FTEs
python orchestrator.py AI_Employee_Vault
```

This generates a Qwen Code prompt.

---

### 4. Process with Qwen Code

Copy the prompt from the orchestrator output, then:

```bash
cd AI_Employee_Vault
qwen
```

Then paste the prompt or say:
```
Process the files in Needs_Action folder using the Company_Handbook rules
```

---

## Full Workflow Example

```bash
# Terminal 1: Start watcher
python watchers/filesystem_watcher.py AI_Employee_Vault

# Terminal 2: Create test file
echo "What action should I take for this?" > AI_Employee_Vault/Drop_Folder\question.txt

# Terminal 3: Run orchestrator (after watcher detects the file)
python orchestrator.py AI_Employee_Vault

# Terminal 3: Copy the output and run qwen
cd AI_Employee_Vault
qwen "Process items in Needs_Action folder"
```

---

## Verify It Works

Check these folders after running:

```bash
# Should have action file
dir AI_Employee_Vault\Needs_Action

# Should have logs
dir AI_Employee_Vault\Logs

# Dashboard should be updated
type AI_Employee_Vault\Dashboard.md
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| "0 new items" | Start watcher BEFORE dropping file |
| Qwen not found | Run `qwen --version` to verify installation |
| No action file created | Check watcher logs in `AI_Employee_Vault/Logs/` |

---

## File Flow

```
Drop_Folder/          →  Needs_Action/      →  Plans/
(you drop here)          (watcher creates)     (qwen creates)
                                                 ↓
Done/                ←  Approved/          ←  Pending_Approval/
(finished)             (you approve)         (needs your OK)
```

---

*For more details, see [README.md](../README.md)*
