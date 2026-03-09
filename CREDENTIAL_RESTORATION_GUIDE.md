# 🔐 Credential Restoration Guide

> **Complete guide to restore Gmail and LinkedIn credentials for Silver Tier**

---

## ⚠️ Why Credentials Were Lost

GitHub's secret scanning detected OAuth credentials in your repository and **blocked the push** to protect your security. The credentials were removed from git history.

---

## 📧 Step 1: Restore Gmail API Credentials

### Option A: Download from Google Cloud Console (Recommended)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project: `za-hackathon-fte` (or create new)

2. **Enable Gmail API**
   - Go to: APIs & Services → Library
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Name: `AI Employee Gmail`
   - Click "Create"

4. **Download credentials.json**
   - Click the download icon (⬇️)
   - Save as `credentials.json`
   - Place in: `C:\Users\user\Documents\GitHub\ZA-Personal-AI-Employee-FTEs\credentials.json`

### Option B: Use Existing Project Credentials

If you already have credentials from before:

1. Check your downloads folder
2. Check your email (Google sends credentials)
3. Check other backup locations

---

## 🔑 Step 2: Authenticate Gmail API

After placing `credentials.json` in project root:

```bash
cd C:\Users\user\Documents\GitHub\ZA-Personal-AI-Employee-FTEs

# Run authentication
python watchers/gmail_watcher.py --authenticate
```

**What happens:**
1. Browser opens automatically
2. Google login page appears
3. Sign in with your Gmail account
4. Grant permissions to the app
5. Browser redirects to localhost
6. `token.json` is created automatically

**Expected output:**
```
Starting Gmail API authentication...
[OK] Authentication successful!
Token saved to: C:\...\token.json
```

---

## 💼 Step 3: Create LinkedIn Credentials (.env)

Create `.env` file in project root:

```bash
# .env file
# LinkedIn Credentials
LINKEDIN_EMAIL=your.email@company.com
LINKEDIN_PASSWORD=your_password

# Optional: LinkedIn Settings
LINKEDIN_MAX_POSTS_PER_DAY=3
LINKEDIN_VAULT_PATH=AI_Employee_Vault

# Gmail Settings
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
GMAIL_CHECK_INTERVAL=120

# WhatsApp Settings
WHATSAPP_CHECK_INTERVAL=30
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help
```

**Replace with your actual credentials:**
- `your.email@company.com` → Your LinkedIn email
- `your_password` → Your LinkedIn password

---

## ✅ Step 4: Verify Credentials

### Test Gmail Connection

```bash
python watchers/gmail_watcher.py --test-connection
```

**Expected output:**
```
[OK] Gmail API connection successful!
     Ready to fetch emails
```

### Test LinkedIn Login

```bash
python watchers/linkedin_poster.py --test-login
```

**Expected output:**
```
Testing LinkedIn login...
[OK] Login successful
Session saved. Future runs will auto-login.
```

### Test WhatsApp Connection

```bash
python watchers/whatsapp_watcher.py --test-connection
```

**Expected output:**
```
Testing WhatsApp Web connection...
A browser window will open. Scan the QR code with your phone.
[OK] Successfully connected!
Session saved. Future runs will auto-login.
```

---

## 🚀 Step 5: Start Silver Tier

Once all credentials are verified:

```bash
# Terminal 1: Gmail Watcher (monitors inbox)
python watchers/gmail_watcher.py AI_Employee_Vault

# Terminal 2: Orchestrator (generates Qwen prompts)
python orchestrator.py AI_Employee_Vault --watch --interval 60

# Terminal 3: Process with Qwen Code
cd AI_Employee_Vault
qwen "Process all items in Needs_Action folder"
```

---

## 🔐 Security Best Practices

### Protected Files (.gitignore)

These files are **automatically excluded** from git:

```
credentials.json     # Gmail API credentials
token.json          # OAuth tokens
.env                # All passwords and secrets
*.log               # Log files
whatsapp_session/   # Browser sessions
linkedin_session/   # Browser sessions
```

### Never Share

- ❌ Never commit `credentials.json` to git
- ❌ Never commit `token.json` to git
- ❌ Never commit `.env` to git
- ❌ Never share screenshots with credentials visible
- ❌ Never post credentials in public forums

### Rotate Credentials

- **Gmail:** Regenerate OAuth credentials every 90 days
- **LinkedIn:** Change password every 90 days
- **Monitor:** Check Google Cloud Console for unusual activity

---

## 🐛 Troubleshooting

### Gmail Authentication Fails

| Error | Solution |
|-------|----------|
| `credentials.json not found` | Download from Google Cloud Console |
| `Invalid client` | Re-download credentials.json |
| `Access blocked` | Enable Gmail API in Google Cloud Console |
| `Token expired` | Run `--authenticate` again |

### LinkedIn Login Fails

| Error | Solution |
|-------|----------|
| `Login failed` | Check email/password in .env |
| `Form not found` | LinkedIn UI changed, update selectors |
| `Session expired` | Delete `linkedin_session/` and re-login |

### WhatsApp QR Code Timeout

| Error | Solution |
|-------|----------|
| `QR code timeout` | Run without `--headless` first |
| `Not connected` | Check internet connection |
| `Session invalid` | Delete `whatsapp_session/` and re-scan |

---

## 📞 Getting Help

### Google Cloud Console Issues

1. Visit: https://support.google.com/googleapi/
2. Check: Gmail API documentation
3. Review: OAuth 2.0 setup guide

### LinkedIn Automation Issues

1. Check: LinkedIn Terms of Service
2. Review: Playwright documentation
3. Test: Manual login first

### General Issues

1. Check: `SILVER_TIER_STATUS.md`
2. Review: `VERIFICATION_REPORT.md`
3. Read: `SILVER_TIER_SETUP.md`

---

## ✅ Credential Restoration Checklist

- [ ] Download `credentials.json` from Google Cloud Console
- [ ] Place in project root
- [ ] Run Gmail authentication
- [ ] Verify `token.json` created
- [ ] Create `.env` file
- [ ] Add LinkedIn credentials to `.env`
- [ ] Test Gmail connection
- [ ] Test LinkedIn login
- [ ] Test WhatsApp connection (optional)
- [ ] Start Gmail Watcher
- [ ] Start Orchestrator
- [ ] Process with Qwen Code

---

**Once all checkboxes are complete, your Silver Tier is fully activated!** 🎉

---

*Powered by Qwen Code*
