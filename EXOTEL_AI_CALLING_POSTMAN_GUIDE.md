# Exotel AI Calling - Postman Collection Guide

Complete Postman collection for testing Exotel AI Calling integration with BookSmart AI.

---

## 📦 Import Collection

### Option 1: Import from JSON (Create this file)

Create file `exotel_ai_calling_postman_collection.json`:

```json
{
  "info": {
    "_postman_id": "exotel-ai-calling-v1",
    "name": "Exotel AI Calling API",
    "description": "Test Exotel webhooks and AI voice calling integration",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Incoming Call Webhook",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/incoming/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "incoming"]
        },
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "CallSid",
              "value": "CA{{$timestamp}}",
              "description": "Unique call ID from Exotel"
            },
            {
              "key": "From",
              "value": "+919999999999",
              "description": "Caller phone number"
            },
            {
              "key": "To",
              "value": "+918888888888",
              "description": "Your Exotel number"
            },
            {
              "key": "Direction",
              "value": "inbound",
              "description": "Call direction"
            }
          ]
        },
        "description": "Simulate incoming call from Exotel. Returns XML with welcome message."
      },
      "response": []
    },
    {
      "name": "2. Gather Input - Speech",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/gather/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "gather"]
        },
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "CallSid",
              "value": "CA{{$timestamp}}",
              "description": "Same CallSid from incoming"
            },
            {
              "key": "SpeechResult",
              "value": "I want to book a haircut appointment tomorrow",
              "description": "Customer speech-to-text"
            },
            {
              "key": "Confidence",
              "value": "0.92",
              "description": "Speech recognition confidence (0-1)"
            },
            {
              "key": "From",
              "value": "+919999999999"
            }
          ]
        },
        "description": "Send speech input to AI. Returns XML with AI response."
      },
      "response": []
    },
    {
      "name": "3. Gather Input - DTMF (Keypad)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/gather/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "gather"]
        },
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "CallSid",
              "value": "CA{{$timestamp}}"
            },
            {
              "key": "Digits",
              "value": "1",
              "description": "Key pressed: 1=Booking, 2=Info, 3=Transfer"
            },
            {
              "key": "From",
              "value": "+919999999999"
            }
          ]
        },
        "description": "Simulate keypad input. 1=Booking, 2=Inquiry, 3=Transfer to human"
      },
      "response": []
    },
    {
      "name": "4. Call Status Callback",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/status/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "status"]
        },
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "CallSid",
              "value": "CA{{$timestamp}}"
            },
            {
              "key": "Status",
              "value": "completed",
              "description": "Options: initiated, ringing, in-progress, completed, failed, busy, no-answer"
            },
            {
              "key": "Duration",
              "value": "180",
              "description": "Call duration in seconds"
            },
            {
              "key": "From",
              "value": "+919999999999"
            },
            {
              "key": "To",
              "value": "+918888888888"
            },
            {
              "key": "StartTime",
              "value": "2024-01-15T10:30:00Z"
            },
            {
              "key": "EndTime",
              "value": "2024-01-15T10:33:00Z"
            }
          ]
        },
        "description": "Update call status. Called multiple times during call lifecycle."
      },
      "response": []
    },
    {
      "name": "5. Recording Callback",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/x-www-form-urlencoded"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/recording/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "recording"]
        },
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "CallSid",
              "value": "CA{{$timestamp}}"
            },
            {
              "key": "RecordingUrl",
              "value": "https://recordings.exotel.com/rec/sample-recording.mp3",
              "description": "URL to download recording"
            },
            {
              "key": "RecordingDuration",
              "value": "175",
              "description": "Recording length in seconds"
            },
            {
              "key": "RecordingChannels",
              "value": "2",
              "description": "1=mono, 2=stereo (both parties)"
            },
            {
              "key": "RecordingStatus",
              "value": "completed"
            }
          ]
        },
        "description": "Receive recording URL after call ends (if recording enabled)"
      },
      "response": []
    },
    {
      "name": "6. Make Outbound Call",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/outbound/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "outbound"]
        },
        "body": {
          "mode": "raw",
          "raw": "{\n  \"phone_number\": \"+919999999999\",\n  \"customer_id\": 123,\n  \"purpose\": \"reminder\",\n  \"message\": \"This is a reminder for your appointment tomorrow at 3 PM\"\n}"
        },
        "description": "Initiate outbound call from your system to customer."
      },
      "response": []
    },
    {
      "name": "7. Send SMS",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/sms/send/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "sms", "send"]
        },
        "body": {
          "mode": "raw",
          "raw": "{\n  \"phone_number\": \"+919999999999\",\n  \"message\": \"Your appointment is confirmed for tomorrow at 3 PM with stylist Priya. BookSmart AI Salon\"\n}"
        },
        "description": "Send SMS notification via Exotel."
      },
      "response": []
    },
    {
      "name": "8. Get Call Details",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/CA123456789/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls", "CA123456789"]
        },
        "description": "Retrieve call details from database."
      },
      "response": []
    },
    {
      "name": "9. List All Calls",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/calls/?limit=10&offset=0",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "calls"],
          "query": [
            {
              "key": "limit",
              "value": "10"
            },
            {
              "key": "offset",
              "value": "0"
            }
          ]
        },
        "description": "List all call logs with pagination."
      },
      "response": []
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://your-ngrok-url.ngrok.io",
      "type": "string"
    },
    {
      "key": "auth_token",
      "value": "your_django_auth_token",
      "type": "string"
    }
  ]
}
```

---

## 🚀 Step-by-Step Testing with Postman

### **Step 1: Setup Environment**

Create Postman Environment:
```json
{
  "name": "Exotel AI Calling - Local",
  "values": [
    {
      "key": "base_url",
      "value": "https://abc123.ngrok.io",
      "enabled": true
    },
    {
      "key": "auth_token",
      "value": "your_django_token_here",
      "enabled": true
    }
  ]
}
```

---

### **Step 2: Start ngrok**

```bash
# Terminal 1: Start Django
python manage.py runserver 8000

# Terminal 2: Start ngrok
ngrok http 8000

# Copy HTTPS URL to Postman environment
```

---

### **Step 3: Test Incoming Call**

**Request:**
```
POST {{base_url}}/api/v1/calls/incoming/
Content-Type: application/x-www-form-urlencoded

CallSid=CA123456789
From=+919999999999
To=+918888888888
Direction=inbound
```

**Expected Response (XML):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Hello! Welcome to BookSmart AI Salon.</Say>
  <Gather action="https://abc123.ngrok.io/api/v1/calls/gather/" input="speech dtmf">
    <Say>How can I help you today?</Say>
  </Gather>
</Response>
```

---

### **Step 4: Test Speech Input**

**Request:**
```
POST {{base_url}}/api/v1/calls/gather/
Content-Type: application/x-www-form-urlencoded

CallSid=CA123456789
SpeechResult=I want to book a haircut tomorrow
Confidence=0.95
From=+919999999999
```

**What Happens:**
1. Your API receives speech text
2. Sends to OpenAI with conversation context
3. AI generates response
4. Returns XML with AI's reply

**Expected Response:**
```xml
<Response>
  <Say>Sure! I can help you book a haircut. What time would work for you?</Say>
  <Gather action="https://abc123.ngrok.io/api/v1/calls/gather/" input="speech">
    <Say>You can say morning, afternoon, or evening.</Say>
  </Gather>
</Response>
```

---

### **Step 5: Test DTMF (Keypad) Input**

**Request:**
```
POST {{base_url}}/api/v1/calls/gather/
Content-Type: application/x-www-form-urlencoded

CallSid=CA123456789
Digits=1
From=+919999999999
```

**Menu Mapping:**
- `1` = Booking
- `2` = Information
- `3` = Transfer to human

---

### **Step 6: Test Status Callback**

**Request:**
```
POST {{base_url}}/api/v1/calls/status/
Content-Type: application/x-www-form-urlencoded

CallSid=CA123456789
Status=completed
Duration=180
From=+919999999999
To=+918888888888
StartTime=2024-01-15T10:30:00Z
EndTime=2024-01-15T10:33:00Z
```

**Expected Response:**
```json
{
  "status": "success"
}
```

---

### **Step 7: Test Recording Callback**

**Request:**
```
POST {{base_url}}/api/v1/calls/recording/
Content-Type: application/x-www-form-urlencoded

CallSid=CA123456789
RecordingUrl=https://recordings.exotel.com/rec/abc123.mp3
RecordingDuration=175
RecordingChannels=2
RecordingStatus=completed
```

---

### **Step 8: Test Outbound Call (Authenticated)**

**Request:**
```
POST {{base_url}}/api/v1/calls/outbound/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
  "phone_number": "+919999999999",
  "customer_id": 123,
  "purpose": "appointment_reminder",
  "message": "Reminder: Your appointment is tomorrow at 3 PM"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "call_sid": "CA987654321",
  "message": "Call initiated to +919999999999"
}
```

---

### **Step 9: Test SMS Send**

**Request:**
```
POST {{base_url}}/api/v1/sms/send/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
  "phone_number": "+919999999999",
  "message": "Your appointment is confirmed for Jan 16 at 3 PM with stylist Priya. Reply CONFIRM to verify."
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message_sid": "SM123456789"
}
```

---

## 📊 Testing Scenarios

### **Scenario 1: Complete Booking Flow**

1. **Incoming Call** → Welcome message
2. **Gather** → "I want to book a haircut"
3. **Gather** → "Tomorrow"
4. **Gather** → "Afternoon"
5. **Gather** → "3 PM"
6. **Gather** → "Confirm"
7. **Status** → Call completed

**Postman Runner:**
```bash
# Use Collection Runner to chain requests
# Save CallSid as variable between requests
```

---

### **Scenario 2: Transfer to Human**

1. **Incoming Call** → Welcome
2. **Gather** → "Talk to a real person"
3. **Gather** → AI detects transfer intent
4. **Response XML** → `<Dial>support_number</Dial>`
5. **Status** → Call transferred

---

### **Scenario 3: Outbound Reminder**

1. **Outbound Call** → API initiates call
2. **Incoming Webhook** → Customer answers
3. **AI** → "Hi John, this is BookSmart AI. Reminder for your appointment tomorrow at 2 PM."
4. **Gather** → "Press 1 to confirm, 2 to reschedule"
5. **Status** → Completed
6. **SMS** → Confirmation sent

---

## 🔍 Debugging in Postman

### **Check Response Headers**

Look for:
```
Content-Type: application/xml    (for webhooks)
Content-Type: application/json    (for API responses)
```

### **Console View**

Press `Ctrl+Alt+C` to see:
- Actual request sent
- Full response
- Timing information

### **Test Scripts (Automated Validation)**

Add to Tests tab:
```javascript
// For webhook endpoints
pm.test("Response is valid XML", function () {
    pm.response.to.have.header("Content-Type");
    pm.expect(pm.response.text()).to.include("<Response>");
});

pm.test("Contains Say tag", function () {
    pm.expect(pm.response.text()).to.include("<Say>");
});

// For JSON endpoints
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success status", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("success");
});
```

---

## 🔄 Collection Runner Workflow

### **Setup Automated Test Flow:**

1. **Pre-request Script** (save variables):
```javascript
// Generate unique CallSid
pm.environment.set("call_sid", "CA" + Date.now());
```

2. **Test Script** (pass data):
```javascript
// Save response data for next request
var xmlResponse = pm.response.text();
pm.environment.set("ai_response", xmlResponse);
```

3. **Run Sequence:**
   - Incoming Call
   - Gather (booking intent)
   - Gather (time selection)
   - Gather (confirmation)
   - Status (completed)

---

## 📱 Mobile Testing

### **Test from Real Phone:**

1. Deploy backend to production
2. Configure Exotel webhooks with production URL
3. Call your Exotel number from mobile
4. Watch Postman/Logs for webhook hits

### **Monitor with Postman Proxy:**

```bash
# View actual Exotel requests
postman-proxy
# Use captured requests to debug
```

---

## 📝 Response Examples

### **AI Conversation Flow**

**Request 1 - Welcome:**
```
POST /api/v1/calls/incoming/
→ Returns: "Hello! Welcome to BookSmart AI..."
```

**Request 2 - Book Intent:**
```
POST /api/v1/calls/gather/
Body: SpeechResult=book appointment
→ Returns: "Sure! What service would you like?"
```

**Request 3 - Service Selection:**
```
POST /api/v1/calls/gather/
Body: SpeechResult=haircut
→ Returns: "Great! When would you like to come?"
```

**Request 4 - Time Selection:**
```
POST /api/v1/calls/gather/
Body: Digits=1  (afternoon option)
→ Returns: "We have 2 PM and 4 PM available..."
```

---

## 🎯 Quick Test Checklist

- [ ] Incoming call returns valid XML
- [ ] XML contains `<Say>` and `<Gather>` tags
- [ ] Speech input triggers AI response
- [ ] DTMF input processed correctly
- [ ] Status callback updates database
- [ ] Recording callback stores URL
- [ ] Outbound call initiates successfully
- [ ] SMS sends correctly
- [ ] Authentication works on protected endpoints
- [ ] Error responses return valid XML

---

## 📚 Resources

- **Postman Download**: https://www.postman.com/downloads/
- **Postman Learning**: https://learning.postman.com/
- **Collection Docs**: https://learning.postman.com/docs/getting-started/importing-and-exporting-data/
- **Exotel API Docs**: https://developer.exotel.com/

---

## 💡 Tips

1. **Save Responses:** Click "Save Response" to compare XML outputs
2. **Environments:** Create separate env for local/production
3. **History:** Use History tab to replay requests quickly
4. **Documentation:** Click "View in Web" to share API docs
5. **Mock Server:** Create mock for testing frontend without backend

---

**Ready to test?** Import the collection, set your ngrok URL, and start calling!
