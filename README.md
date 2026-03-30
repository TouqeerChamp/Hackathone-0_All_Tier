# 🤖 Personal AI Employee (FTE) - Hackathon 0

## Autonomous Task Management & Email Processing System

**Version:** 2.0.0  
**Last Updated:** March 30, 2026  
**Author:** Mohammad Touqeer  
**Project:** Hackathon 0 (My AI Employee)

---

## 📋 Executive Summary

The **Personal AI Employee** is an intelligent, autonomous agent system designed to act as your virtual full-time employee (FTE). It continuously monitors your Gmail inbox, processes incoming tasks using AI-powered reasoning, categorizes them by complexity, supports **Roman Urdu** for broader accessibility, and generates executive CEO briefings.

### 🎯 Lenovo X260 i5 Optimization

This system is **specifically engineered** to run efficiently on modest hardware—the **Lenovo ThinkPad X260 with Intel i5 processor**. Every architectural decision prioritizes:

- **Minimal CPU usage** - Background processes consume <1% CPU at idle
- **Low memory footprint** - Total system runs on ~150MB RAM (Platinum Tier)
- **Fast startup** - Services initialize in <5 seconds
- **Local-first processing** - No cloud dependencies for core functionality
- **Native Python execution** - Avoids Docker overhead for 70% resource reduction

This optimization makes the AI Employee accessible to small businesses and individuals without requiring expensive cloud infrastructure.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Bronze     │────▶│    Silver    │────▶│     Gold     │   │
│  │    Tier      │     │     Tier     │     │     Tier     │   │
│  │              │     │              │     │              │   │
│  │ • File-based │     │ • Gmail API  │     │ • Docker     │   │
│  │ • Local AI   │     │ • LinkedIn   │     │ • Odoo ERP   │   │
│  │ • Dashboard  │     │ • Auto-reply │     │ • Micro-     │   │
│  │              │     │              │     │   services   │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                ▼                                │
│                      ┌──────────────────┐                      │
│                      │   Platinum Tier  │                      │
│                      │   (Production)   │                      │
│                      │                  │                      │
│                      │ • Lightweight    │                      │
│                      │ • Always-On      │                      │
│                      │ • Executive Dash │                      │
│                      │ • 31 Email Test  │                      │
│                      └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Tier Comparison

| Feature | Bronze | Silver | Gold | Platinum |
|---------|--------|--------|------|----------|
| **Inbox Monitoring** | ✅ File-based | ✅ Gmail API | ✅ Gmail API | ✅ Gmail API |
| **AI Categorization** | ✅ Local | ✅ Local | ✅ Local | ✅ Local |
| **Roman Urdu Support** | ✅ | ✅ | ✅ | ✅ |
| **Dashboard** | ✅ Basic | ✅ Enhanced | ✅ Real-time | ✅ Executive |
| **LinkedIn Automation** | ❌ | ✅ | ✅ | ✅ |
| **Odoo ERP Integration** | ❌ | ❌ | ✅ | ✅ |
| **Deployment** | Manual | Manual | Docker | Native Python |
| **Always-On** | ❌ | ❌ | ✅ | ✅ Optimized |
| **Memory Usage** | ~50MB | ~75MB | ~500MB | ~150MB |
| **Startup Time** | <1s | <1s | 30-60s | <5s |
| **Executive Briefing** | ✅ Basic | ✅ Enhanced | ✅ Weekly | ✅ Real-time |
| **Health Monitoring** | ❌ | ❌ | Basic | ✅ Heartbeat |
| **Autonomous Cleanup** | ❌ | ❌ | ❌ | ✅ Full |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **Lenovo X260 i5** or equivalent (minimum: 4GB RAM, dual-core CPU)
- Gmail API credentials (for Silver tier and above)
- Anthropic API key (for AI-powered categorization)

### Installation

1. **Choose your tier** based on requirements:
   - **Bronze**: Basic file-based task processing
   - **Silver**: Gmail + LinkedIn automation
   - **Gold**: Full ERP integration with Docker
   - **Platinum**: Production-ready lightweight always-on

2. **Navigate to tier folder**:
   ```bash
   cd Bronze_Tier    # or Silver_Tier, Gold_Tier, Platinum_Tier
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   
   # Edit .env with your API keys
   ```

5. **Run the system**:
   ```bash
   python watcher.py
   ```

---

## 📁 Folder Structure

```
Hackathon_0(My_AI_Employee)/
├── README.md                 # This file
├── .env.example              # Environment variables template
├── Bronze_Tier/              # Basic tier - file-based processing
│   ├── README.md
│   ├── watcher.py
│   ├── briefing.py
│   ├── CLAUDE.md
│   ├── Dashboard.md
│   ├── inbox/                # Tasks awaiting processing
│   ├── needs_action/         # Complex tasks requiring action
│   ├── done/                 # Completed tasks
│   └── logs/                 # System logs
├── Silver_Tier/              # Gmail + LinkedIn automation
│   ├── README.md
│   ├── gmail_watcher.py
│   ├── linkedin_automation.py
│   └── ...
├── Gold_Tier/                # Docker + Odoo ERP
│   ├── README.md
│   ├── docker-compose.yml
│   ├── odoo_client.py
│   └── ...
└── Platinum_Tier/            # Production-ready always-on
    ├── README.md
    ├── executive_dashboard.py
    ├── heartbeat.py
    ├── autonomous_agent.py
    └── ...
```

---

## 🎯 Core Features

### 1. **Inbox Monitoring**
Continuously scans for new tasks via file system (Bronze) or Gmail API (Silver+).

### 2. **AI-Powered Categorization**
Distinguishes between 'simple' and 'complex' tasks using Claude AI reasoning.

### 3. **Roman Urdu Support**
Unique multilingual capability for South Asian language support.

### 4. **Automated Dashboard**
Real-time statistics and folder counts for monitoring system status.

### 5. **CEO Briefings**
Executive summaries generated automatically with key metrics.

### 6. **Workflow Management**
Organized task flow through inbox → needs_action → done pipeline.

### 7. **LinkedIn Automation** (Silver+)
Automated connection request handling and draft responses.

### 8. **Odoo ERP Integration** (Gold+)
Customer record creation and CRM synchronization.

### 9. **Executive Dashboard** (Platinum)
Real-time 24/7 health monitoring with 10-minute status updates.

### 10. **Heartbeat Monitoring** (Platinum)
Always-on service health checks with failure detection.

---

## 🛠️ Agent Skills

All tiers implement the core skills defined in `CLAUDE.md`:

| Skill | Description |
|-------|-------------|
| **Inbox Monitoring** | Scan inbox folder for pending tasks |
| **Task Categorization** | Distinguish 'simple' vs 'complex' tasks using AI |
| **Dashboard Management** | Update Dashboard.md with folder counts |
| **CEO Reporting** | Generate executive summaries via briefing.py |

### Execution Flow

```
1. Scan /inbox folder
        ↓
2. Read and categorize each task
        ↓
3. Update Dashboard.md statistics
        ↓
4. Run briefing.py for summary
        ↓
5. Move tasks to appropriate folders
```

---

## 📝 Configuration

### Environment Variables

Create a `.env` file in your tier folder:

```bash
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Gmail OAuth (Silver+)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.pickle

# Odoo ERP (Gold+)
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_API_KEY=your_api_key

# Model Configuration
CLAUDE_MODEL=claude-3-sonnet-20240229

# Processing Settings
CHECK_INTERVAL=300  # Seconds between inbox checks
```

**See `.env.example`** for a complete template with all required variables.

---

## 🎯 Use Cases

### Small Business Owner
- **Tier**: Platinum
- **Benefit**: Always-on email processing without cloud costs
- **Hardware**: Lenovo X260 i5 runs 24/7 at ~150MB RAM

### Freelancer
- **Tier**: Silver
- **Benefit**: Automated LinkedIn outreach and email management
- **Hardware**: Any laptop with Python 3.8+

### Startup
- **Tier**: Gold
- **Benefit**: Full CRM integration with Odoo
- **Hardware**: Docker-capable server or local machine

### Developer Testing
- **Tier**: Bronze
- **Benefit**: Quick local testing without API dependencies
- **Hardware**: Any Python environment

---

## 📊 Performance Metrics

### Platinum Tier (Optimized for Lenovo X260 i5)

| Metric | Value | Notes |
|--------|-------|-------|
| **Memory Usage** | ~150MB | 70% reduction vs Docker |
| **CPU Idle** | 0.5-1% | Minimal background load |
| **Startup Time** | <5 seconds | Native Python venv |
| **Email Processing** | 31 emails tested | Full audit trail |
| **Disk Usage** | ~500MB | No container overhead |

### Resource Optimization Strategies

1. **Native Python Processes** - Avoid Docker container overhead
2. **Virtual Environment** - Isolated dependencies without bloat
3. **Parallel Background Services** - Independent, lightweight processes
4. **Efficient Polling** - 5-minute intervals balance responsiveness and resource usage
5. **Local-First Architecture** - Minimize cloud API calls where possible

---

## 🔒 Security & Privacy

- **Local Processing**: All task data stored locally on your machine
- **OAuth 2.0**: Secure Gmail API authentication
- **Encrypted Tokens**: API credentials stored securely
- **No Data Sharing**: Your emails and tasks never leave your system
- **Audit Trail**: Complete logging of all processing actions

---

## 📚 Documentation by Tier

| Tier | README | Architecture | Deployment |
|------|--------|--------------|------------|
| **Bronze** | [README](Bronze_Tier/README.md) | - | Manual |
| **Silver** | [README](Silver_Tier/README.md) | - | Manual |
| **Gold** | [README](Gold_Tier/README.md) | [ARCHITECTURE](Gold_Tier/ARCHITECTURE.md) | Docker |
| **Platinum** | [README](Platinum_Tier/README.md) | [PLATINUM_ARCHITECTURE](Platinum_Tier/PLATINUM_ARCHITECTURE.md) | Native Python |

---

## 🧪 Testing

Each tier includes test files for validation:

```bash
# Run tests for your tier
cd Platinum_Tier
python test_watcher.py
python test_direct_search.py
python test_json_parsing.py
```

### Platinum Tier Test Results
- ✅ 31 emails processed successfully
- ✅ 12 categorized as needs_action
- ✅ 19 categorized as done
- ✅ 3 new Odoo customers created
- ✅ 0 processing errors

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Test thoroughly** on Lenovo X260 i5 or equivalent hardware
4. **Document changes** in the appropriate tier README
5. **Submit a pull request** with detailed description

---

## 📄 License

[Specify your license here - MIT/Apache 2.0 recommended]

---

## 🙏 Acknowledgments

- **Anthropic** for Claude AI integration
- **Google** for Gmail API and OAuth
- **Odoo** for open-source ERP capabilities
- **Lenovo** for the reliable X260 i5 development platform

---

## 📞 Support

For issues, questions, or feature requests, please open an issue in the repository.

**Developed with ❤️ for efficient, accessible AI automation on modest hardware.**

---

## 🏆 Project Status

| Tier | Status | Notes |
|------|--------|-------|
| **Bronze** | ✅ Complete | Core functionality operational |
| **Silver** | ✅ Complete | Gmail + LinkedIn automation |
| **Gold** | ✅ Complete | Docker + Odoo integration |
| **Platinum** | ✅ Complete | Production-ready, 31-email tested |

**Last Audit:** March 30, 2026
