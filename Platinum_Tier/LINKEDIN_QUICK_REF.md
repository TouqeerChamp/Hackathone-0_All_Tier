# 🚀 LinkedIn Automation - Quick Reference

## ⚡ One-Time Setup

```bash
# Authenticate with LinkedIn (do this ONCE)
python linkedin_auth.py
```

## 📬 Daily Use

```bash
# Run full AI Employee automation (Email + Odoo + LinkedIn)
python autonomous_agent.py

# Or use batch file
run_ai_employee.bat
```

## 🧪 Testing

```bash
# Test LinkedIn posting with sample data
python linkedin_automation.py
```

## 📝 What Gets Posted

```
Today my AI Employee (on Lenovo X260) processed X emails and updated Odoo! #GIAIC #AI_Employee 🚀🤖
```

## 🎯 Expected Output

```
4. Posting to LinkedIn (Real-Time Direct Posting)...
   Message: Today my AI Employee (on Lenovo X260) processed 5 emails...
   ✓ LinkedIn Post ID: linkedin_20260401123456
   ✓ Post published LIVE on LinkedIn!
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not logged in" error | Run `python linkedin_auth.py` |
| Post saved to drafts | Check `linkedin_drafts/` folder |
| Authentication expired | Delete `linkedin_cookies.json` and re-authenticate |

## 📂 Key Files

- `linkedin_auth.py` - Authentication helper
- `linkedin_automation.py` - Direct posting logic
- `linkedin_cookies.json` - Session cookies (auto-generated)
- `autonomous_agent.py` - Main automation (updated)

## ✅ Success Checklist

- [ ] Playwright installed (`pip install playwright`)
- [ ] Chromium installed (`playwright install chromium`)
- [ ] Authenticated (`python linkedin_auth.py`)
- [ ] Cookies saved (`linkedin_cookies.json` exists)
- [ ] Run automation (`python autonomous_agent.py`)
- [ ] Post visible on LinkedIn profile

---

**100% Zero-Manual-Work Achieved! 🎉**
