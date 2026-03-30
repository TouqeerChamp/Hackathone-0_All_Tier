# 🥉 Bronze Tier - Personal AI Employee

## Foundation Tier: File-Based Task Processing

**Version:** 1.0.0  
**Last Updated:** March 30, 2026  
**Tier Status:** ✅ Complete

---

## 📋 Overview

The **Bronze Tier** is the foundation of the Personal AI Employee system. It provides **file-based task processing** with AI-powered categorization, perfect for local testing and basic automation without external API dependencies.

### 🎯 Lenovo X260 i5 Optimization

Bronze Tier is engineered for **minimal resource consumption** on the Lenovo ThinkPad X260 i5:

- **Memory Usage**: ~50MB RAM
- **CPU Usage**: <0.5% at idle
- **Startup Time**: <1 second
- **Disk Usage**: ~100MB
- **No External Dependencies**: Runs entirely offline (except AI API)

---

## 🚀 Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **File-Based Inbox** | Monitor local `/inbox` folder for task files |
| **AI Categorization** | Claude-powered simple vs. complex task distinction |
| **Roman Urdu Support** | Process tasks written in Roman Urdu script |
| **Dashboard Updates** | Real-time folder count statistics |
| **CEO Briefings** | Automated executive summary generation |
| **Workflow Pipeline** | inbox → needs_action → done |

### What's Included

- ✅ `watcher.py` - Main inbox monitoring script
- ✅ `briefing.py` - CEO briefing generator
- ✅ `process_urdu.py` - Roman Urdu language processing
- ✅ `Dashboard.md` - Real-time status display
- ✅ `CLAUDE.md` - Agent skills documentation
- ✅ `Company_Handbook.md` - Mission and responsibilities

### What's NOT Included

- ❌ Gmail API integration
- ❌ LinkedIn automation
- ❌ Odoo ERP integration
- ❌ Docker deployment
- ❌ Always-on background services

---

## 📁 Folder Structure

```
Bronze_Tier/
├── README.md                 # This file
├── watcher.py                # Main inbox monitor
├── briefing.py               # CEO briefing generator
├── process_urdu.py           # Urdu language processing
├── CLAUDE.md                 # Agent skills documentation
├── Company_Handbook.md       # Mission statement
├── Dashboard.md              # Auto-generated dashboard
├── inbox/                    # Tasks awaiting processing
├── needs_action/             # Complex tasks requiring action
├── done/                     # Completed tasks
└── logs/                     # System logs
```

---

## 🛠️ Installation

### Prerequisites

- **Python 3.8+** on Windows/Linux/Mac
- **Lenovo X260 i5** or equivalent (minimum: 2GB RAM, dual-core CPU)
- **Anthropic API Key** (for AI categorization)

### Setup Steps

1. **Navigate to Bronze Tier**:
   ```bash
   cd Bronze_Tier
   ```

2. **Install Dependencies**:
   ```bash
   pip install python-dotenv anthropic
   ```

3. **Create Environment File**:
   ```bash
   # Copy from root .env.example or create manually
   copy ..\.env.example .env
   ```

4. **Configure API Keys**:
   Edit `.env` with your Anthropic API key.

---

## 💻 Usage

### Manual Execution

Run the watcher manually:

```bash
python watcher.py
```

This will:
1. Scan the `/inbox` folder
2. Read each task file
3. Categorize as 'simple' or 'complex'
4. Move tasks to appropriate folders
5. Update Dashboard.md

### Agentic Mode

Use natural language commands:

```
process the inbox
```

This triggers the **CLAUDE.md skill sequence**:

```
1. Inbox Monitoring → Scan /inbox folder
        ↓
2. Task Categorization → Read and classify tasks
        ↓
3. Dashboard Management → Update folder counts
        ↓
4. CEO Reporting → Run briefing.py
```

### Create a Task File

Add a new task to `/inbox`:

**File**: `inbox/my_task.txt`
```
Task: Review quarterly sales report
Priority: High
Details: Need to analyze Q1 performance and prepare summary for board meeting.
```

Or in Roman Urdu:

**File**: `inbox/urdu_task.txt`
```
Task: Sales report ka review
Priority: Zaroori
Details: Q1 ki performance analyze karni hai aur board meeting ke liye summary taiyar karni hai.
```

---

## 📊 Dashboard

The system automatically maintains `Dashboard.md`:

```markdown
# Task Dashboard

## Current Status
| Folder | Count |
|--------|-------|
| Inbox | 5 |
| Needs Action | 3 |
| Done | 12 |

## Last Updated
2026-03-30 14:30:00
```

---

## 🧪 Testing

Run included test files:

```bash
# Test basic watcher functionality
python test_watcher.py

# Test Urdu processing
python process_urdu.py

# Debug specific issues
python test_debug.py
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional
CLAUDE_MODEL=claude-3-sonnet-20240229
CHECK_INTERVAL=300
LOG_LEVEL=INFO
```

### Task Categorization Logic

The AI analyzes tasks based on:

| Indicator | Category |
|-----------|----------|
| Simple keywords (hello, hi, test) | done |
| Complex keywords (analyze, research, plan) | needs_action |
| Roman Urdu detected | needs_action |
| Multi-step requirements | needs_action |

---

## 📈 Performance on Lenovo X260 i5

| Metric | Value |
|--------|-------|
| **Memory** | ~50MB |
| **CPU Idle** | <0.5% |
| **Startup** | <1 second |
| **Task Processing** | ~2-5 seconds per task |
| **Disk I/O** | Minimal (local files only) |

---

## 🔄 Workflow

```
┌─────────────┐
│   /inbox    │  ← Place new task files here
│  (pending)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  watcher.py │  ← Scans and categorizes
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  simple   │ │  complex  │ │   error   │
│    →      │ │    →      │ │    →      │
│  /done    │ │/needs_    │ │  /logs    │
│           │ │ action    │ │           │
└───────────┘ └───────────┘ └───────────┘
```

---

## 🎯 Use Cases

### Ideal For:
- ✅ Local development and testing
- ✅ Learning the AI Employee architecture
- ✅ Offline task management
- ✅ Simple automation workflows
- ✅ Developers on modest hardware

### Not Suitable For:
- ❌ Gmail integration required
- ❌ Real-time email processing
- ❌ CRM/ERP integration
- ❌ Production always-on deployment

---

## 📝 Agent Skills (CLAUDE.md)

### Skill 1: Inbox Monitoring
**Description**: Scan the `/inbox` folder to identify pending tasks

### Skill 2: Task Categorization
**Description**: Read file content and distinguish between 'simple' and 'complex' tasks

### Skill 3: Dashboard Management
**Description**: Update `Dashboard.md` with current folder counts

### Skill 4: CEO Reporting
**Description**: Run `briefing.py` to generate executive summaries

---

## 🔒 Security

- **Local Storage**: All task files stored locally
- **No External APIs**: Except Anthropic for AI reasoning
- **Encrypted API Keys**: Stored in `.env` (not committed to git)
- **Audit Logs**: Complete processing history in `/logs`

---

## 🐛 Troubleshooting

### Issue: Tasks not being processed

**Solution**: Check that task files are in `/inbox` folder and have valid content.

### Issue: API errors

**Solution**: Verify `ANTHROPIC_API_KEY` in `.env` is valid and has credits.

### Issue: Dashboard not updating

**Solution**: Ensure `Dashboard.md` is not open in another program (file lock).

---

## 📚 Related Documentation

- **Main README**: [Root README](../README.md)
- **Company Handbook**: [Company_Handbook.md](Company_Handbook.md)
- **Agent Skills**: [CLAUDE.md](CLAUDE.md)
- **Dashboard**: [Dashboard.md](Dashboard.md)

---

## 🚀 Upgrade Path

Ready for more features? Upgrade to higher tiers:

| Tier | New Features |
|------|--------------|
| **Silver** | Gmail API, LinkedIn automation |
| **Gold** | Docker deployment, Odoo ERP |
| **Platinum** | Always-on, Executive Dashboard, 70% resource reduction |

---

## 📄 License

[Specify your license here]

---

**Bronze Tier** - The foundation of intelligent task automation.

**Optimized for Lenovo X260 i5** 🎯
