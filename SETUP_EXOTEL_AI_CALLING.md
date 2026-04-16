# Exotel AI Calling Integration - Setup Guide

Complete setup guide for integrating Exotel cloud telephony with AI-powered voice agents for BookSmart AI.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Exotel Account Setup](#exotel-account-setup)
3. [Backend Configuration](#backend-configuration)
4. [Environment Variables](#environment-variables)
5. [API Endpoints](#api-endpoints)
6. [AI Integration](#ai-integration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **Exotel Account**: Sign up at [Exotel](https://my.exotel.com/)
- **Python Backend**: Django/FastAPI server running
- **Public URL**: Ngrok or deployed domain for webhooks
- **OpenAI API Key**: For AI processing
- **Indian Phone Number**: For testing (Exotel works best with Indian numbers)

---

## Exotel Account Setup

### Step 1: Create Account

1. Visit [my.exotel.com](https://my.exotel.com/)
2. Sign up with your business email
3. Complete KYC verification (required for Indian numbers)
4. Choose a plan (Start with "Build" plan for testing)

### Step 2: Get API Credentials

1. Navigate to **Settings** → **API Settings**
2. Generate new API Key
3. Note these credentials:
   - Account SID
   - API Key
   - API Token
   - Exophone Number

```bash
# Save these in your .env file
EXOTEL_ACCOUNT_SID=your_account_sid_here
EXOTEL_API_KEY=your_api_key_here
EXOTEL_API_TOKEN=your_api_token_here
EXOTEL_EXOPHONE=+91XXXXXXXXXX
```

### Step 3: Purchase Exophone Number

1. Go to **Numbers** → **Buy Number**
2. Select:
   - Country: India
   - Type: Virtual Number
   - Capabilities: Voice + SMS
3. Note the purchased number

### Step 4: Create Exotel App

1. Navigate to **App Bazaar** → **Create New App**
2. Select **"Connect"** as the flow type
3. Configure Webhook URLs:
   - **Call Request URL**: `https://your-api.com/api/v1/calls/incoming/`
   - **Status Callback URL**: `https://your-api.com/api/v1/calls/status/`
   - **Recording Callback URL**: `https://your-api.com/api/v1/calls/recording/`

---

## Backend Configuration

### Step 1: Install Dependencies

```bash
pip install exotel openai django-cors-headers
```

### Step 2: Update settings.py

```python
# settings.py

# Exotel Configuration
EXOTEL_ACCOUNT_SID = os.getenv('EXOTEL_ACCOUNT_SID')
EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY')
EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN')
EXOTEL_EXOPHONE = os.getenv('EXOTEL_EXOPHONE')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Backend URL for webhooks
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Installed Apps
INSTALLED_APPS = [
    # ... existing apps
    'corsheaders',
]

# Middleware
MIDDLEWARE = [
    # ... existing middleware
    'corsheaders.middleware.CorsMiddleware',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://my.exotel.com",
]
```

### Step 3: Create Database Models

```python
# models/call.py
from django.db import models
from django.utils import timezone

class CallLog(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('busy', 'Busy'),
        ('no-answer', 'No Answer'),
    ]
    
    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    call_sid = models.CharField(max_length=100, unique=True)
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='initiated')
    
    # AI Conversation
    ai_transcript = models.TextField(null=True, blank=True)
    ai_response = models.TextField(null=True, blank=True)
    
    # Recording
    recording_url = models.URLField(null=True, blank=True)
    recording_duration = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # User association (if customer exists)
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'call_logs'
        ordering = ['-created_at']

class CallRecording(models.Model):
    call = models.ForeignKey(CallLog, on_delete=models.CASCADE, related_name='recordings')
    recording_url = models.URLField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ConversationContext(models.Model):
    """Store conversation context for AI continuity"""
    call = models.OneToOneField(CallLog, on_delete=models.CASCADE, related_name='context')
    context_data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
```

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Exotel Service

```python
# services/exotel_service.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ExotelService:
    """
    Exotel API integration service
    """
    
    def __init__(self):
        self.account_sid = settings.EXOTEL_ACCOUNT_SID
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.exophone = settings.EXOTEL_EXOPHONE
        self.base_url = f"https://api.exotel.com/v1/Accounts/{self.account_sid}"
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated request to Exotel API"""
        url = f"{self.base_url}/{endpoint}"
        auth = (self.api_key, self.api_token)
        
        try:
            if method == 'GET':
                response = requests.get(url, auth=auth, timeout=30)
            else:
                response = requests.post(url, data=data, auth=auth, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Exotel API error: {str(e)}")
            raise
    
    def make_call(self, to_number, flow_url=None, caller_id=None, custom_field=None):
        """
        Make an outbound call
        
        Args:
            to_number: Customer phone number (+91XXXXXXXXXX)
            flow_url: URL with XML/JSON flow
            caller_id: From number (defaults to exophone)
            custom_field: Custom data to track
        """
        payload = {
            'From': to_number,
            'CallerId': caller_id or self.exophone,
            'CallType': 'trans',  # transactional
            'Url': flow_url or f"{settings.BACKEND_URL}/api/v1/calls/flow/",
            'CustomField': custom_field or '',
            'StatusCallback': f"{settings.BACKEND_URL}/api/v1/calls/status/",
            'RecordingCallback': f"{settings.BACKEND_URL}/api/v1/calls/recording/",
        }
        
        return self._make_request('POST', 'Calls/connect.json', payload)
    
    def send_sms(self, to_number, message, sender_id=None):
        """
        Send SMS via Exotel
        """
        payload = {
            'From': sender_id or self.exophone,
            'To': to_number,
            'Body': message[:1600],  # Exotel limit
        }
        
        return self._make_request('POST', 'Sms/send.json', payload)
    
    def get_call_details(self, call_sid):
        """
        Get call details by SID
        """
        return self._make_request('GET', f'Calls/{call_sid}.json')
    
    def hangup_call(self, call_sid):
        """
        Hangup an active call
        """
        payload = {'Status': 'completed'}
        return self._make_request('POST', f'Calls/{call_sid}.json', payload)
    
    def redirect_call(self, call_sid, new_url):
        """
        Redirect an active call to new flow URL
        """
        payload = {'Url': new_url}
        return self._make_request('POST', f'Calls/{call_sid}.json', payload)
```

### Step 5: Create AI Service

```python
# services/ai_voice_service.py
import openai
from django.conf import settings
from django.core.cache import cache
import json
import logging

logger = logging.getLogger(__name__)

class AIVoiceService:
    """
    AI-powered voice conversation handler
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4"
    
    def get_system_prompt(self):
        """Get system prompt for salon booking AI"""
        return """You are an AI voice assistant for BookSmart AI, a salon booking system.
Your role is to help customers with:
1. Booking appointments
2. Checking service availability
3. Answering questions about services and pricing
4. Providing salon information (hours, location, etc.)
5. Rescheduling or canceling appointments

IMPORTANT INSTRUCTIONS FOR VOICE:
- Keep responses VERY concise (1-2 sentences max)
- Speak naturally and warmly
- Ask one question at a time
- Confirm information before proceeding
- Use simple language, avoid technical terms
- If you don't understand, politely ask them to repeat

CONVERSATION FLOW:
1. Greet and ask how you can help
2. Listen to their request
3. Ask clarifying questions if needed
4. Confirm details before booking
5. Provide booking confirmation with details
6. Offer additional help

SALON SERVICES:
- Haircut & Styling
- Hair Coloring
- Facial & Skin Care
- Manicure & Pedicure
- Massage Therapy
- Bridal Packages

BUSINESS HOURS:
- Monday-Saturday: 10 AM - 8 PM
- Sunday: 11 AM - 6 PM

If customer asks to speak to a human, say you'll transfer them and end the call professionally."""
    
    def get_conversation_history(self, call_sid):
        """Get conversation history from cache"""
        key = f"call_context_{call_sid}"
        return cache.get(key, [])
    
    def save_conversation_history(self, call_sid, history):
        """Save conversation history to cache (30 min expiry)"""
        key = f"call_context_{call_sid}"
        cache.set(key, history, timeout=1800)
    
    def process_input(self, call_sid, user_input, customer_context=None):
        """
        Process user voice input and generate AI response
        
        Args:
            call_sid: Unique call identifier
            user_input: Speech-to-text or DTMF input
            customer_context: Customer data if available
        
        Returns:
            dict with response message and action
        """
        try:
            # Get conversation history
            history = self.get_conversation_history(call_sid)
            
            # Add system prompt if new conversation
            if not history:
                history = [{"role": "system", "content": self.get_system_prompt()}]
                if customer_context:
                    history.append({
                        "role": "system", 
                        "content": f"Customer Info: {json.dumps(customer_context)}"
                    })
            
            # Add user input
            history.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=history,
                max_tokens=100,  # Keep responses short for voice
                temperature=0.7,
            )
            
            ai_message = response.choices[0].message.content
            
            # Add AI response to history
            history.append({"role": "assistant", "content": ai_message})
            self.save_conversation_history(call_sid, history)
            
            # Determine action
            action = self._determine_action(ai_message, user_input)
            
            return {
                'message': ai_message,
                'action': action,
                'call_sid': call_sid,
                'should_continue': action != 'hangup'
            }
            
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return {
                'message': "I'm sorry, I'm having trouble understanding. Could you please repeat that?",
                'action': 'retry',
                'call_sid': call_sid,
                'should_continue': True
            }
    
    def _determine_action(self, ai_message, user_input):
        """Determine next action based on conversation"""
        user_lower = user_input.lower()
        ai_lower = ai_message.lower()
        
        # Check for hangup signals
        if any(phrase in ai_lower for phrase in ['goodbye', 'thank you for calling', 'have a great day']):
            return 'hangup'
        
        # Check for transfer request
        if any(phrase in user_lower for phrase in ['speak to human', 'talk to manager', 'representative', 'real person']):
            return 'transfer'
        
        # Check for booking intent
        if any(phrase in user_lower for phrase in ['book', 'appointment', 'schedule', 'slot', 'reserve']):
            return 'booking'
        
        # Check for cancellation
        if any(phrase in user_lower for phrase in ['cancel', 'delete', 'remove']):
            return 'cancellation'
        
        # Check for inquiry
        if any(phrase in user_lower for phrase in ['price', 'cost', 'how much', 'available', 'timing']):
            return 'inquiry'
        
        return 'continue'
    
    def generate_ssml(self, text):
        """
        Generate SSML for better voice synthesis (optional)
        """
        # Add pauses and emphasis for natural speech
        ssml = f"""<speak>
            {text.replace('.', '<break time="300ms"/>')}
        </speak>"""
        return ssml
```

---

## API Endpoints

### Step 6: Create Call Views

```python
# views/calls.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
from ..services.exotel_service import ExotelService
from ..services.ai_voice_service import AIVoiceService
from ..models import CallLog
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def create_response_xml(message, action='continue', gather_input=True):
    """
    Create Exotel XML response
    """
    response = ET.Element('Response')
    
    # Add message
    if message:
        say = ET.SubElement(response, 'Say')
        say.text = message
    
    # Add gather for next input if needed
    if action == 'continue' and gather_input:
        gather = ET.SubElement(response, 'Gather')
        gather.set('action', f"{settings.BACKEND_URL}/api/v1/calls/gather/")
        gather.set('method', 'POST')
        gather.set('input', 'speech dtmf')
        gather.set('speechTimeout', 'auto')
        gather.set('numDigits', '1')
        gather.set('finishOnKey', '#')
        
        # Add hint
        say_hint = ET.SubElement(gather, 'Say')
        say_hint.text = "Please speak or press a key."
    
    elif action == 'hangup':
        ET.SubElement(response, 'Hangup')
    
    elif action == 'transfer':
        dial = ET.SubElement(response, 'Dial')
        dial.text = settings.SUPPORT_PHONE_NUMBER or settings.EXOTEL_EXOPHONE
    
    return ET.tostring(response, encoding='unicode')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def incoming_call(request):
    """
    Handle incoming calls from Exotel
    """
    try:
        # Extract call data
        call_sid = request.data.get('CallSid')
        from_number = request.data.get('From')
        to_number = request.data.get('To')
        
        logger.info(f"Incoming call from {from_number}, SID: {call_sid}")
        
        # Create call log
        call_log, created = CallLog.objects.get_or_create(
            call_sid=call_sid,
            defaults={
                'from_number': from_number,
                'to_number': to_number,
                'direction': 'incoming',
                'status': 'ringing'
            }
        )
        
        # Check if customer exists
        customer = None
        try:
            customer = Customer.objects.get(phone=from_number)
            call_log.customer = customer
            call_log.save()
        except Customer.DoesNotExist:
            pass
        
        # Welcome message
        welcome_msg = "Hello! Welcome to BookSmart AI Salon. I'm your AI assistant. How can I help you today?"
        
        # Generate XML response
        xml_response = create_response_xml(welcome_msg, 'continue', gather_input=True)
        
        return HttpResponse(xml_response, content_type='application/xml')
        
    except Exception as e:
        logger.error(f"Error in incoming_call: {str(e)}")
        error_xml = create_response_xml(
            "Sorry, we're experiencing technical difficulties. Please try again later.",
            'hangup'
        )
        return HttpResponse(error_xml, content_type='application/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def call_gather(request):
    """
    Handle user input (speech or DTMF) from Exotel
    """
    try:
        call_sid = request.data.get('CallSid')
        digits = request.data.get('Digits')
        speech_result = request.data.get('SpeechResult')
        confidence = request.data.get('Confidence', 0)
        
        # Use speech if available, otherwise digits
        user_input = speech_result or digits or ''
        
        logger.info(f"Gather input received - Call: {call_sid}, Input: {user_input}")
        
        if not user_input:
            # No input received, ask again
            xml_response = create_response_xml(
                "I didn't catch that. Could you please speak again?",
                'continue'
            )
            return HttpResponse(xml_response, content_type='application/xml')
        
        # Get call and customer context
        try:
            call_log = CallLog.objects.get(call_sid=call_sid)
            customer_context = None
            if call_log.customer:
                customer_context = {
                    'name': call_log.customer.name,
                    'last_visit': str(call_log.customer.last_visit) if call_log.customer.last_visit else None,
                }
        except CallLog.DoesNotExist:
            call_log = None
            customer_context = None
        
        # Process with AI
        ai_service = AIVoiceService()
        ai_result = ai_service.process_input(call_sid, user_input, customer_context)
        
        # Update call log with transcript
        if call_log:
            if call_log.ai_transcript:
                call_log.ai_transcript += f"\nUser: {user_input}"
                call_log.ai_response += f"\nAI: {ai_result['message']}"
            else:
                call_log.ai_transcript = f"User: {user_input}"
                call_log.ai_response = f"AI: {ai_result['message']}"
            call_log.save()
        
        # Generate XML response
        xml_response = create_response_xml(
            ai_result['message'],
            ai_result['action'],
            gather_input=ai_result['should_continue']
        )
        
        return HttpResponse(xml_response, content_type='application/xml')
        
    except Exception as e:
        logger.error(f"Error in call_gather: {str(e)}")
        error_xml = create_response_xml(
            "Sorry, I didn't understand that. Could you try again?",
            'continue'
        )
        return HttpResponse(error_xml, content_type='application/xml')


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def call_status_callback(request):
    """
    Handle call status updates from Exotel
    """
    try:
        call_sid = request.data.get('CallSid')
        status = request.data.get('Status')
        recording_url = request.data.get('RecordingUrl')
        
        logger.info(f"Call status update - SID: {call_sid}, Status: {status}")
        
        # Update call log
        try:
            call_log = CallLog.objects.get(call_sid=call_sid)
            call_log.status = status.lower()
            
            if recording_url:
                call_log.recording_url = recording_url
            
            if status in ['completed', 'failed', 'busy', 'no-answer']:
                from django.utils import timezone
                call_log.ended_at = timezone.now()
                
                # Clear conversation cache
                from django.core.cache import cache
                cache.delete(f"call_context_{call_sid}")
            
            call_log.save()
            
        except CallLog.DoesNotExist:
            logger.warning(f"CallLog not found for SID: {call_sid}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error in call_status_callback: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def call_recording_callback(request):
    """
    Handle recording callback from Exotel
    """
    try:
        call_sid = request.data.get('CallSid')
        recording_url = request.data.get('RecordingUrl')
        duration = request.data.get('RecordingDuration')
        
        logger.info(f"Recording received - SID: {call_sid}, URL: {recording_url}")
        
        # Update call log
        try:
            call_log = CallLog.objects.get(call_sid=call_sid)
            call_log.recording_url = recording_url
            call_log.recording_duration = int(duration) if duration else None
            call_log.save()
            
            # Create separate recording record
            CallRecording.objects.create(
                call=call_log,
                recording_url=recording_url,
                duration=int(duration) if duration else 0
            )
            
        except CallLog.DoesNotExist:
            logger.warning(f"CallLog not found for recording: {call_sid}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error in call_recording_callback: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)


# views/outbound_calls.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..services.exotel_service import ExotelService
from ..models import Customer, CallLog
from django.utils import timezone

@api_view(['POST'])
def make_outbound_call(request):
    """
    Initiate outbound call to customer
    """
    try:
        customer_id = request.data.get('customer_id')
        phone_number = request.data.get('phone_number')
        purpose = request.data.get('purpose', 'reminder')  # reminder, confirmation, promotion
        
        # Get phone number
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            phone_number = customer.phone
        
        if not phone_number:
            return Response({'error': 'Phone number required'}, status=400)
        
        # Initialize Exotel service
        exotel = ExotelService()
        
        # Make call
        result = exotel.make_call(
            to_number=phone_number,
            custom_field=purpose
        )
        
        # Create call log
        call_sid = result.get('Call', {}).get('Sid')
        if call_sid:
            CallLog.objects.create(
                call_sid=call_sid,
                from_number=settings.EXOTEL_EXOPHONE,
                to_number=phone_number,
                direction='outgoing',
                status='initiated',
                customer=customer if customer_id else None
            )
        
        return Response({
            'status': 'success',
            'call_sid': call_sid,
            'message': f'Call initiated to {phone_number}'
        })
        
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)
    except Exception as e:
        logger.error(f"Error making outbound call: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def send_sms_notification(request):
    """
    Send SMS notification via Exotel
    """
    try:
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        
        if not phone_number or not message:
            return Response({'error': 'Phone and message required'}, status=400)
        
        exotel = ExotelService()
        result = exotel.send_sms(phone_number, message)
        
        return Response({
            'status': 'success',
            'message_sid': result.get('SMSMessage', {}).get('Sid')
        })
        
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return Response({'error': str(e)}, status=500)
```

### Step 7: Add URLs

```python
# urls.py
from django.urls import path
from .views import calls, outbound_calls

urlpatterns = [
    # Incoming call webhooks (public, no auth required)
    path('api/v1/calls/incoming/', calls.incoming_call, name='incoming-call'),
    path('api/v1/calls/gather/', calls.call_gather, name='call-gather'),
    path('api/v1/calls/status/', calls.call_status_callback, name='call-status'),
    path('api/v1/calls/recording/', calls.call_recording_callback, name='call-recording'),
    
    # Outbound calls (authenticated)
    path('api/v1/calls/outbound/', outbound_calls.make_outbound_call, name='outbound-call'),
    path('api/v1/sms/send/', outbound_calls.send_sms_notification, name='send-sms'),
]
```

---

## Environment Variables

### .env file:

```bash
# Exotel Configuration
EXOTEL_ACCOUNT_SID=your_account_sid_here
EXOTEL_API_KEY=your_api_key_here
EXOTEL_API_TOKEN=your_api_token_here
EXOTEL_EXOPHONE=+91XXXXXXXXXX

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_key_here

# Backend Configuration
BACKEND_URL=https://your-ngrok-url.ngrok.io
DEBUG=True

# Support phone (for transfers)
SUPPORT_PHONE_NUMBER=+91XXXXXXXXXX

# Django Secret
SECRET_KEY=your_django_secret_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## Testing

### Test with ngrok:

```bash
# 1. Start ngrok
ngrok http 8000

# 2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# 3. Update BACKEND_URL in .env
# 4. Restart Django server

# 5. Test incoming call webhook
curl -X POST https://your-ngrok.ngrok.io/api/v1/calls/incoming/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test123" \
  -d "From=+919999999999" \
  -d "To=+918888888888"

# 6. Test gather endpoint
curl -X POST https://your-ngrok.ngrok.io/api/v1/calls/gather/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test123" \
  -d "SpeechResult=I want to book an appointment"
```

### Exotel Dashboard Testing:

1. Go to Exotel Dashboard → Numbers
2. Click on your Exophone number
3. Configure webhooks with ngrok URL
4. Click "Test" button
5. Enter your phone number and receive test call

---

## Troubleshooting

### Common Issues:

| Issue | Solution |
|-------|----------|
| Webhook not receiving calls | Check ngrok is running, verify URL in Exotel dashboard |
| SSL certificate error | Use HTTPS URL (ngrok provides this) |
| AI not responding | Check OpenAI API key, verify quota not exceeded |
| Call dropping immediately | Check XML response is valid, no syntax errors |
| Speech not recognized | Verify Gather configuration accepts speech input |
| 403 Forbidden | Add `corsheaders` and whitelist Exotel IPs |

### Debug Mode:

```python
# Add to settings.py for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Production Deployment

### Checklist:

- [ ] Valid SSL certificate (Let's Encrypt)
- [ ] Production domain (not ngrok)
- [ ] Update webhook URLs in Exotel dashboard
- [ ] Set DEBUG=False
- [ ] Configure proper logging
- [ ] Add rate limiting (django-ratelimit)
- [ ] Monitor call quality metrics
- [ ] Setup alerts for failed calls
- [ ] Implement call retry logic
- [ ] Backup conversation data
- [ ] GDPR/privacy compliance for recordings

---

## Resources

- **Exotel API Docs**: https://developer.exotel.com/
- **Exotel Python SDK**: https://github.com/sarathsp06/exotel-py
- **Voice XML Reference**: https://developer.exotel.com/voice-xml
- **OpenAI API Docs**: https://platform.openai.com/docs

---

## Support

For issues:
1. Check Exotel Dashboard logs
2. Review Django application logs
3. Contact Exotel support: support@exotel.com
4. OpenAI status: https://status.openai.com/
