# 📞 Exotel Integration Setup Guide

## 🚀 Overview
BookSmart AI now supports **Exotel** for SMS and voice services, replacing Twilio. Exotel provides better coverage in India and more competitive pricing for Indian businesses.

## 🔧 Configuration

### 1. Get Exotel Credentials
1. Sign up at [Exotel Dashboard](https://dashboard.exotel.com/)
2. Get your Account SID, API Key, and API Token from Settings → API
3. Purchase an Exotel virtual number for SMS and voice calls

### 2. Update Environment Variables
Add these to your `.env` file:

```bash
# ─── Exotel SMS & Voice ──────────────────────────────────────
EXOTEL_ACCOUNT_SID=your_exotel_account_sid
EXOTEL_API_KEY=your_exotel_api_key  
EXOTEL_API_TOKEN=your_exotel_api_token
EXOTEL_PHONE_NUMBER=+91your_exotel_number
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 📋 Features

### 📨 SMS Services
- **Booking Confirmations**: Automatic SMS when customers book appointments
- **Appointment Reminders**: Daily reminders for appointments within 24 hours
- **Custom Messages**: Support for personalized SMS content

### 📞 Voice Services
- **Incoming Calls**: AI-powered virtual receptionist answers calls
- **Outbound Calls**: Automated appointment reminders via voice
- **Real-time Processing**: Speech-to-text and text-to-speech integration

## 🛠 API Endpoints

### SMS Endpoints
```http
# SMS is handled automatically via booking creation
POST /bookings/  # Sends booking confirmation SMS

# Manual reminder trigger
POST /reminders/trigger  # Sends reminders for upcoming appointments
```

### Voice Endpoints
```http
# Exotel webhook for incoming calls
POST /exotel/incoming-call

# Call status updates
POST /exotel/call-status

# Make outbound calls
POST /exotel/make-call
Content-Type: application/x-www-form-urlencoded

customer_number=+91XXXXXXXXXX&message=Your custom message

# Voice app configuration
GET /exotel/app-config

# WebSocket for real-time voice processing
WS /exotel/ws/exotel-voice
```

## 🎯 Exotel App Configuration

### Step 1: Create Exotel App
1. Go to Exotel Dashboard → Apps
2. Create new app named `booksmart_voice_app`
3. Set App URL to: `http://your-domain.com/exotel/incoming-call`
4. Set Status URL to: `http://your-domain.com/exotel/call-status`
5. Choose your preferred voice settings

### Step 2: Configure Phone Number
1. Go to Phone Numbers in Exotel Dashboard
2. Select your virtual number
3. Set the Voice App to `booksmart_voice_app`
4. Configure SMS settings if needed

## 🔄 Migration from Twilio

### What Changed
- ✅ **SMS**: `twilio_client.py` → `exotel_client.py`
- ✅ **Voice**: `voice_handler.py` → `exotel_voice_handler.py`
- ✅ **Environment**: `TWILIO_*` → `EXOTEL_*`
- ✅ **API Routes**: `/voice/*` → `/exotel/*`

### Compatibility
- All existing booking and reminder functionality works unchanged
- SMS content and timing remain the same
- Voice AI features (STT/TTS) are preserved

## 🧪 Testing

### Mock Mode (No API Keys Required)
```bash
# Test without Exotel credentials
EXOTEL_ACCOUNT_SID=mock_exotel_sid
EXOTEL_API_KEY=mock_api_key
EXOTEL_API_TOKEN=mock_api_token
```

### Test SMS
```python
from exotel_client import send_booking_sms
result = await send_booking_sms("+919876543210", "John Doe", "Haircut", "2026-04-08 10:00 AM")
print(result)
```

### Test Voice
```bash
# Check voice app config
curl http://localhost:8000/exotel/app-config

# Test webhook (simulate Exotel call)
curl -X POST http://localhost:8000/exotel/incoming-call \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+919876543210&To=+91XXXXXXXXXX&CallSid=test123&CallStatus=ringing"
```

## 📊 Monitoring

### Logs
All Exotel operations are logged with `[Exotel]` prefix:
- SMS sending status
- Call initiation results
- WebSocket connection events
- Error details

### Dashboard Integration
The frontend dashboard automatically uses Exotel for:
- Booking confirmations
- Reminder scheduling
- Voice call handling

## 🔒 Security

### API Key Management
- Store Exotel credentials securely in environment variables
- Never commit API keys to version control
- Use different keys for development and production

### Number Verification
- Verify your Exotel numbers are properly configured
- Test with small volumes before full deployment
- Monitor Exotel dashboard for usage patterns

## 📞 Support

### Exotel Documentation
- [Exotel API Docs](https://developer.exotel.com/)
- [SMS API Guide](https://developer.exotel.com/api/sms)
- [Voice API Guide](https://developer.exotel.com/api/voice)

### Troubleshooting
1. **SMS not sending**: Check API credentials and number verification
2. **Voice issues**: Verify webhook URLs and app configuration
3. **WebSocket errors**: Check firewall and SSL certificate settings

## 💰 Pricing

### Exotel Rates (India)
- **SMS**: ~₹0.25 per SMS
- **Voice**: ~₹0.75 per minute
- **Virtual Number**: ~₈000/month

### Cost Optimization
- Use SMS for confirmations, voice for complex queries
- Implement smart retry logic for failed deliveries
- Monitor usage patterns to optimize messaging

---

**🎉 Your BookSmart AI is now powered by Exotel!**

For support, check the Exotel dashboard or contact their support team.
