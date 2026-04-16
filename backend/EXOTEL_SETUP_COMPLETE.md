# Exotel AI Calling - Complete Setup Guide

## ✅ YOUR CURRENT STATUS

### ✅ Already Configured:
- Exotel Account SID: ✓ Set
- Exotel API Key: ✓ Set  
- Exotel API Token: ✓ Set
- Exotel App ID: ✓ Set
- Exotel Phone Number: ✓ Set (09513886363)

### ⚠️ Missing:
- **GROQ_API_KEY** - Needed for AI responses (get free at groq.com)

---

## 🚀 QUICK START (3 Steps)

### Step 1: Get Groq API Key (2 mins)
1. Visit https://console.groq.com/
2. Sign up with Google/GitHub
3. Click "API Keys" → "Create API Key"
4. Copy the key

### Step 2: Add to .env (1 min)
Open `c:\Users\abish\OneDrive\Desktop\aa\booksmart-ai\backend\.env` and add:
```
GROQ_API_KEY=gsk_YOUR_GROQ_KEY_HERE
```

### Step 3: Run the System (1 min)
Double-click: `c:\Users\abish\OneDrive\Desktop\aa\booksmart-ai\backend\start_exotel_ai.bat`

This will:
- Start the backend server
- Start ngrok tunnel
- Show configuration instructions

---

## 📋 DETAILED SETUP

### 1. INSTALL NGROK (One-time)

**Option A - Download:**
- https://ngrok.com/download
- Extract ngrok.exe to any folder
- Add to PATH or run from backend folder

**Option B - Chocolatey:**
```powershell
choco install ngrok
ngrok authtoken YOUR_NGROK_TOKEN
```

**Get Authtoken:**
1. Sign up at https://ngrok.com/
2. Go to Dashboard → Your Authtoken
3. Copy and run: `ngrok authtoken YOUR_TOKEN`

---

### 2. EXOTEL DASHBOARD CONFIGURATION

**Login:** https://my.exotel.com/

**Navigate:**
Numbers → Your Exophone (09513886363) → Edit

**Configure These URLs:**

| Setting | URL (replace YOUR-NGROK with actual URL) |
|---------|------------------------------------------|
| **Call Request URL** | `https://YOUR-NGROK.ngrok.io/exotel/incoming` |
| **Status Callback URL** | `https://YOUR-NGROK.ngrok.io/exotel/status` |
| **Recording URL** | `https://YOUR-NGROK.ngrok.io/exotel/recording` |
| **Method** | POST |

**Click SAVE**

---

### 3. VERIFY SETUP

**Test Endpoints:**

1. **Incoming Call Handler**
```bash
curl -X POST https://YOUR-NGROK.ngrok.io/exotel/incoming \
  -d "CallSid=TEST123" \
  -d "From=+919999999999" \
  -d "To=09513886363"
```

Expected: XML response with "Welcome to BookSmart AI Salon"

2. **Speech Input Handler**
```bash
curl -X POST https://YOUR-NGROK.ngrok.io/exotel/gather \
  -d "CallSid=TEST123" \
  -d "SpeechResult=I want to book a haircut tomorrow" \
  -d "Confidence=0.95"
```

Expected: XML response with slot availability

---

## 📞 LIVE TESTING

### Call Your Exotel Number: **09513886363**

**Sample Conversation:**
```
You: Call 09513886363
AI: Hello! Welcome to BookSmart AI Salon. I'm your virtual assistant. How can I help you today?

You: I want to book a haircut
AI: I'd be happy to help you book a haircut. When would you like to come?

You: Tomorrow
AI: We have 43 slots open tomorrow. Available times: 10:00 AM, 11:30 AM, 2:00 PM. Which works for you?

You: 2 PM
AI: Great! 2 PM is available. Which stylist would you prefer? Priya, Rahul, or Anita all do haircuts.

You: Priya
AI: Priya is available at 2 PM. May I have your name?

You: John
AI: Thank you John. What's your phone number?

You: 9876543210
AI: Let me confirm: Haircut with Priya tomorrow at 2 PM. Name: John, Phone: 9876543210. Is this correct?

You: Yes
AI: Perfect! Your booking is confirmed. Reference: BK20250115143215. See you tomorrow at 2 PM!
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: "AI not responding"
**Check:**
```bash
# Test backend is running
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### Issue 2: "Exotel can't reach webhook"
**Check ngrok is running:**
```bash
ngrok http 8000
# Look for HTTPS URL in terminal
```

### Issue 3: "AI responses are slow"
**Solution:** Verify GROQ_API_KEY is set in .env

### Issue 4: "Call connects but no AI voice"
**Check Exotel dashboard URLs:**
- Must use HTTPS (not HTTP)
- Must end with `/exotel/incoming`
- Must include full ngrok domain

---

## 📊 API ENDPOINTS AVAILABLE

### Public Webhooks (Exotel calls these):
```
POST /exotel/incoming     - Handle new calls
POST /exotel/gather       - Process speech/DTMF
POST /exotel/status       - Track call status
POST /exotel/recording    - Receive recordings
```

### Management APIs (Authenticated):
```
POST /exotel/outbound     - Make outbound calls
POST /exotel/sms          - Send SMS
GET  /exotel/calls        - List call history
GET  /exotel/config       - Get configuration
```

---

## 💰 COST BREAKDOWN

| Service | Cost |
|---------|------|
| Exotel Exophone | ₹0-500/month |
| Incoming Calls | ₹0.40-0.60/minute |
| Outgoing Calls | ₹0.50-0.70/minute |
| Groq AI | Free tier: 1M tokens/day |
| Ngrok | Free tier (temporary URLs) |

---

## 🔐 SECURITY CHECKLIST

- [ ] .env file has correct credentials
- [ ] JWT_SECRET_KEY changed from default
- [ ] Exotel dashboard URLs use HTTPS
- [ ] ngrok authtoken is set
- [ ] Groq API key is kept secret

---

## 📱 NEXT STEPS

1. **Add more stylists** in `ai_voice_service.py` SALON_CONFIG
2. **Customize services** and pricing
3. **Add SMS confirmations** after booking
4. **Set up call recording** in Exotel dashboard
5. **Add analytics** to track call metrics

---

## 🆘 SUPPORT

**Exotel Issues:**
- Email: support@exotel.com
- Docs: https://developer.exotel.com/

**Backend Issues:**
- Check logs in terminal
- Test at: http://localhost:8000/docs

**AI Issues:**
- Verify GROQ_API_KEY
- Check groq.com dashboard for usage

---

## ✅ FINAL VERIFICATION

Before going live, verify:

1. [ ] Backend runs: `python main.py`
2. [ ] Ngrok shows HTTPS URL
3. [ ] Exotel dashboard has correct URLs
4. [ ] Test call connects to AI
5. [ ] AI responds with greeting
6. [ ] AI checks slots when booking
7. [ ] AI confirms booking with reference

**Ready to receive customer calls! 🎉**
