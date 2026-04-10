"""
Exotel Applet Logic - Complete Implementation
Handles all 6 applet types: Greeting, Gather, Passthru, Connect, SMS, Hangup
"""
from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import Response, JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from database import get_db
from models import CallLog, CallRecording, Booking
from ai_voice_service import (
    process_voice_input, 
    get_booking_context, 
    clear_booking_context,
    check_slot_availability,
    get_service_info,
    SALON_CONFIG
)
from exotel_client import exotel_client
from config import settings
from datetime import datetime
from security_middleware import is_exotel_ip
import xml.etree.ElementTree as ET
import logging
import json
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exotel", tags=["Exotel Applets"])


def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number format."""
    if not phone:
        return False
    # Remove spaces, dashes, + prefix
    cleaned = re.sub(r'[\s\-+]', '', phone)
    # Must be 10 digits starting with 6-9
    return bool(re.match(r'^[6-9]\d{9}$', cleaned))


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection."""
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>&\"\']', '', text)
    # Limit length
    return sanitized[:500]


def mask_call_sid(call_sid: str) -> str:
    """Mask call SID for logging."""
    if not call_sid or len(call_sid) < 8:
        return "****"
    return f"{call_sid[:4]}****{call_sid[-4:]}"


def create_xml_response(message: str = None, action: str = "continue", 
                       gather_input: bool = False, transfer_number: str = None,
                       sms_message: str = None, to_number: str = None) -> str:
    """
    Create Exotel XML response for all applet types.
    
    Actions:
    - 'greeting': Just say message
    - 'gather': Say message + collect input
    - 'passthru': Send data to webhook
    - 'connect': Transfer to number
    - 'sms': Send text message
    - 'hangup': End call
    """
    response = ET.Element("Response")
    
    # Add message if provided
    if message:
        say = ET.SubElement(response, "Say")
        say.set("voice", "woman")
        say.set("language", "en-IN")
        say.text = message
    
    # Handle different applet actions
    if action == "gather" or gather_input:
        gather = ET.SubElement(response, "Gather")
        gather.set("action", f"/exotel/applet/gather")
        gather.set("method", "POST")
        gather.set("input", "speech dtmf")
        gather.set("speechTimeout", "auto")
        gather.set("numDigits", "1")
        gather.set("finishOnKey", "#")
        
        prompt = ET.SubElement(gather, "Say")
        prompt.set("voice", "woman")
        prompt.text = "Please speak after the beep, or press a key."
    
    elif action == "connect" and transfer_number:
        dial = ET.SubElement(response, "Dial")
        dial.text = transfer_number
        
    elif action == "sms" and sms_message and to_number:
        sms = ET.SubElement(response, "Sms")
        sms.set("to", to_number)
        sms.text = sms_message
        
    elif action == "hangup":
        ET.SubElement(response, "Hangup")
    
    elif action == "passthru":
        # Passthru is handled internally, just continue
        redirect = ET.SubElement(response, "Redirect")
        redirect.set("method", "POST")
        redirect.text = "/exotel/applet/gather"
    
    return ET.tostring(response, encoding="unicode")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 1: GREETING
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/greeting")
async def applet_greeting(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Applet 1: GREETING
    Initial welcome message when customer calls.
    Flow: Greeting → Gather
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized greeting access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize inputs
        call_sid = sanitize_input(CallSid)
        from_num = sanitize_input(From)
        to_num = sanitize_input(To)
        
        logger.info(f"[Greeting] Call from {mask_call_sid(from_num)}, SID: {mask_call_sid(call_sid)}")
        
        # Create call log
        call_log = CallLog(
            call_sid=call_sid,
            from_number=from_num,
            to_number=to_num,
            direction="incoming",
            status="in-progress",
            created_at=datetime.utcnow()
        )
        db.add(call_log)
        db.commit()
        
        # Welcome message with service options
        welcome_msg = (
            "Hello! Welcome to BookSmart AI Salon. "
            "I'm your virtual assistant. I can help you book appointments, "
            "check availability, or answer questions. What would you like to do?"
        )
        
        # Return XML: Greeting + Gather (collect intent)
        xml_response = create_xml_response(
            message=welcome_msg,
            action="gather"
        )
        
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Greeting Error] {str(e)}")
        error_xml = create_xml_response(
            message="Welcome to BookSmart AI. How can I help?",
            action="gather"
        )
        return Response(content=error_xml, media_type="application/xml")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 2: GATHER (Collect Speech/DTMF Input)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/gather")
async def applet_gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    Digits: str = Form(default=""),
    Confidence: float = Form(default=0.0),
    From: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Applet 2: GATHER
    Process speech/DTMF input and route to appropriate handler.
    This is the MAIN AI processing applet.
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized gather access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize all inputs
        call_sid = sanitize_input(CallSid)
        user_input = sanitize_input(SpeechResult) if SpeechResult else sanitize_input(Digits)
        from_num = sanitize_input(From)
        
        # Log with masked data
        logger.info(f"[Gather] Call: {mask_call_sid(call_sid)}, Input length: {len(user_input)}")
        
        if not user_input:
            # No input received
            xml_response = create_xml_response(
                message="I didn't catch that. Could you please repeat?",
                action="gather"
            )
            return Response(content=xml_response, media_type="application/xml")
        
        # Get booking context
        context = get_booking_context(call_sid)
        
        # Process with AI
        ai_result = process_voice_input(call_sid, user_input)
        ai_message = sanitize_input(ai_result["message"])
        action = ai_result["action"]
        context = ai_result.get("booking_context", context)
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
        if call_log:
            if call_log.ai_transcript:
                call_log.ai_transcript += f"\nUser: {user_input}"
                call_log.ai_response += f"\nAI: {ai_message}"
            else:
                call_log.ai_transcript = f"User: {user_input}"
                call_log.ai_response = f"AI: {ai_message}"
            
            # Update booking details from context
            if context.get("service"):
                call_log.service = context["service"]
            if context.get("date"):
                call_log.date = context["date"]
            if context.get("time"):
                call_log.time = context["time"]
            if context.get("stylist"):
                call_log.stylist = context["stylist"]
            if context.get("customer_name"):
                call_log.customer_name = context["customer_name"]
            if context.get("phone"):
                call_log.phone = context["phone"]
            if context.get("booking_reference"):
                call_log.booking_reference = context["booking_reference"]
            
            db.commit()
        
        # Determine next action based on booking stage
        if action == "hangup" or context.get("stage") == "confirmed":
            # Booking complete - send SMS and hangup
            if context.get("phone") and context.get("booking_reference"):
                # Validate phone before sending SMS
                phone = context["phone"]
                if validate_phone_number(phone):
                    sms_msg = (
                        f"BookSmart AI: Booking confirmed! "
                        f"Ref: {context['booking_reference'][:20]}. "
                        f"Service: {context.get('service', 'N/A')[:30]} at "
                        f"{context.get('time', 'N/A')[:10]}. See you then!"
                    )
                    xml_response = create_xml_response(
                        message=ai_message,
                        action="sms",
                        sms_message=sms_msg,
                        to_number=phone
                    )
                else:
                    xml_response = create_xml_response(
                        message=ai_message,
                        action="hangup"
                    )
            else:
                xml_response = create_xml_response(
                    message=ai_message,
                    action="hangup"
                )
            
            # Clear context
            clear_booking_context(call_sid)
            
        elif action == "transfer":
            # Transfer to human
            xml_response = create_xml_response(
                message=ai_message + " Please hold while I transfer you.",
                action="connect",
                transfer_number=settings.EXOTEL_PHONE_NUMBER
            )
            
        elif action in ["booking", "booking_in_progress", "continue"]:
            # Continue conversation - gather more input
            xml_response = create_xml_response(
                message=ai_message,
                action="gather"
            )
        
        else:
            # Default: continue gathering
            xml_response = create_xml_response(
                message=ai_message,
                action="gather"
            )
        
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't expose internal details
        logger.error(f"[Gather Error] {str(e)}")
        error_xml = create_xml_response(
            message="I'm sorry, I didn't understand. Could you try again?",
            action="gather"
        )
        return Response(content=error_xml, media_type="application/xml")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 3: PASSTHRU (Send Data to External Webhook)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/passthru")
async def applet_passthru(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(default="in-progress"),
    CustomField: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Applet 3: PASSTHRU
    Send call data to external system.
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized passthru access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize inputs
        call_sid = sanitize_input(CallSid)
        custom = sanitize_input(CustomField)
        
        logger.info(f"[Passthru] Call {mask_call_sid(call_sid)}, Status: {CallStatus}")
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
        if call_log:
            call_log.status = sanitize_input(CallStatus)
            if custom:
                call_log.custom_data = custom
            db.commit()
        
        xml_response = create_xml_response(message=None, action="passthru")
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Passthru Error] {str(e)}")
        return Response(content="<Response><Hangup/></Response>", media_type="application/xml")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 4: CONNECT (Transfer Call)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/connect")
async def applet_connect(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    transfer_to: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Applet 4: CONNECT
    Transfer call to human agent.
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized connect access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize inputs
        call_sid = sanitize_input(CallSid)
        transfer_num = sanitize_input(transfer_to)
        
        # Validate transfer number
        if transfer_num and not validate_phone_number(transfer_num):
            logger.error(f"Invalid transfer number: {transfer_num}")
            transfer_num = settings.EXOTEL_PHONE_NUMBER
        
        logger.info(f"[Connect] Transferring call {mask_call_sid(call_sid)}")
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
        if call_log:
            call_log.status = "transferred"
            call_log.transferred_to = transfer_num or settings.EXOTEL_PHONE_NUMBER
            db.commit()
        
        transfer_number = transfer_num or settings.EXOTEL_PHONE_NUMBER
        xml_response = create_xml_response(
            message="Please hold while I connect you.",
            action="connect",
            transfer_number=transfer_number
        )
        
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Connect Error] {str(e)}")
        return Response(
            content="<Response><Say>Unable to transfer. Please call back later.</Say><Hangup/></Response>",
            media_type="application/xml"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 5: SMS (Send Text Message)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/sms")
async def applet_sms(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    message: str = Form(default=""),
    phone_number: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Applet 5: SMS
    Send SMS confirmation.
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized SMS access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize inputs
        call_sid = sanitize_input(CallSid)
        target = sanitize_input(phone_number) or sanitize_input(From)
        sms_msg = sanitize_input(message) or "Thank you for calling BookSmart AI Salon!"
        
        # Validate phone number
        if not validate_phone_number(target):
            logger.error(f"Invalid phone number for SMS: {target}")
            xml_response = create_xml_response(
                message="Unable to send confirmation. Goodbye!",
                action="hangup"
            )
            return Response(content=xml_response, media_type="application/xml")
        
        # Limit SMS length
        sms_msg = sms_msg[:160]  # Standard SMS limit
        
        logger.info(f"[SMS] Sending to {target[:6]}****: {sms_msg[:30]}...")
        
        # Send via Exotel client
        result = await exotel_client.send_sms(target, sms_msg)
        
        # Log SMS
        if result:
            call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
            if call_log:
                call_log.sms_sent = True
                call_log.sms_message = sms_msg[:200]  # Limit storage
                db.commit()
        
        xml_response = create_xml_response(
            message="Confirmation message sent to your phone.",
            action="hangup"
        )
        
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SMS Error] {str(e)}")
        xml_response = create_xml_response(
            message="Thank you for calling. Goodbye!",
            action="hangup"
        )
        return Response(content=xml_response, media_type="application/xml")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLET 6: HANGUP (End Call)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/applet/hangup")
async def applet_hangup(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallDuration: str = Form(default="0"),
    RecordingUrl: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Applet 6: HANGUP
    End the call and save final details.
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized hangup access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Sanitize inputs
        call_sid = sanitize_input(CallSid)
        duration = sanitize_input(CallDuration)
        recording = sanitize_input(RecordingUrl)
        
        # Validate duration is numeric
        try:
            duration_int = int(duration) if duration else 0
        except ValueError:
            duration_int = 0
        
        logger.info(f"[Hangup] Call {mask_call_sid(call_sid)} ended. Duration: {duration_int}s")
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
        if call_log:
            call_log.status = "completed"
            call_log.ended_at = datetime.utcnow()
            call_log.duration = duration_int
            
            if recording:
                call_log.recording_url = recording
            
            db.commit()
            
            # Save recording record
            if recording:
                rec = CallRecording(
                    call_id=call_log.id,
                    recording_url=recording,
                    duration=duration_int
                )
                db.add(rec)
                db.commit()
        
        # Clear booking context
        clear_booking_context(call_sid)
        
        xml_response = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Hangup/></Response>"
        return Response(content=xml_response, media_type="application/xml")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Hangup Error] {str(e)}")
        return Response(
            content="<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Hangup/></Response>",
            media_type="application/xml"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE CALL FLOW ENDPOINT (Handles all applets in sequence)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/flow")
async def complete_flow(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(default="ringing"),
    SpeechResult: str = Form(default=""),
    Digits: str = Form(default=""),
    step: str = Query(default="greeting"),
    db: Session = Depends(get_db)
):
    """
    COMPLETE FLOW - Single endpoint that handles all applet types
    """
    try:
        # Security: Verify request from Exotel
        client_ip = request.client.host
        if not is_exotel_ip(client_ip):
            logger.warning(f"Unauthorized flow access from {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Validate step parameter
        valid_steps = ["greeting", "gather", "passthru", "connect", "sms", "hangup"]
        if step not in valid_steps:
            step = "greeting"
        
        logger.info(f"[Flow] Step: {step}, Call: {mask_call_sid(sanitize_input(CallSid))}")
        
        # Route to appropriate applet
        if step == "greeting":
            return await applet_greeting(request, CallSid, From, To, db)
        elif step == "gather":
            return await applet_gather(request, CallSid, SpeechResult, Digits, 0.0, From, db)
        elif step == "passthru":
            return await applet_passthru(request, CallSid, From, To, CallStatus, "", db)
        elif step == "connect":
            return await applet_connect(request, CallSid, From, To, "", db)
        elif step == "sms":
            return await applet_sms(request, CallSid, From, To, "", "", db)
        elif step == "hangup":
            return await applet_hangup(request, CallSid, From, To, "0", "", db)
        else:
            return await applet_greeting(request, CallSid, From, To, db)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Flow Error] {str(e)}")
        return Response(
            content="<Response><Say>System error. Please try again later.</Say><Hangup/></Response>",
            media_type="application/xml"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS FOR MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/calls/{call_sid}")
async def get_call_details(call_sid: str, db: Session = Depends(get_db)):
    """Get details of a specific call."""
    call = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
    if not call:
        return JSONResponse({"status": "error", "message": "Call not found"}, status_code=404)
    
    return JSONResponse({
        "status": "success",
        "call": {
            "call_sid": call.call_sid,
            "from_number": call.from_number,
            "to_number": call.to_number,
            "status": call.status,
            "service": call.service,
            "date": call.date,
            "time": call.time,
            "stylist": call.stylist,
            "customer_name": call.customer_name,
            "phone": call.phone,
            "booking_reference": call.booking_reference,
            "ai_transcript": call.ai_transcript,
            "created_at": call.created_at.isoformat() if call.created_at else None,
            "ended_at": call.ended_at.isoformat() if call.ended_at else None
        }
    })


@router.get("/calls")
async def list_calls(
    limit: int = 50,
    offset: int = 0,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List all calls with filters."""
    query = db.query(CallLog)
    
    if status:
        query = query.filter(CallLog.status == status)
    
    total = query.count()
    calls = query.order_by(CallLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return JSONResponse({
        "status": "success",
        "total": total,
        "calls": [
            {
                "call_sid": c.call_sid,
                "from_number": c.from_number,
                "status": c.status,
                "service": c.service,
                "customer_name": c.customer_name,
                "booking_reference": c.booking_reference,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in calls
        ]
    })


@router.post("/outbound")
async def make_outbound_call(
    phone_number: str,
    message: str = "Hello from BookSmart AI!",
    flow_url: str = None,
    db: Session = Depends(get_db)
):
    """Initiate outbound call via Exotel."""
    try:
        result = await exotel_client.make_call(
            to_number=phone_number,
            app_name=settings.EXOTEL_APP_ID
        )
        
        if result:
            return JSONResponse({
                "status": "success",
                "call_sid": result.get("Call", {}).get("Sid"),
                "message": f"Call initiated to {phone_number}"
            })
        else:
            return JSONResponse(
                {"status": "error", "message": "Failed to initiate call"},
                status_code=500
            )
            
    except Exception as e:
        # Log error but don't expose internal details to response
        logger.error(f"[Outbound Error] {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Failed to initiate call"},
            status_code=500
        )


@router.get("/config")
async def get_applet_config():
    """Get configuration for Exotel applet setup."""
    return JSONResponse({
        "status": "success",
        "applets": {
            "greeting": {
                "url": "/exotel/applet/greeting",
                "method": "POST",
                "description": "Initial welcome message"
            },
            "gather": {
                "url": "/exotel/applet/gather",
                "method": "POST",
                "description": "Collect speech/DTMF input with AI processing"
            },
            "passthru": {
                "url": "/exotel/applet/passthru",
                "method": "POST",
                "description": "Send data to external webhook"
            },
            "connect": {
                "url": "/exotel/applet/connect",
                "method": "POST",
                "description": "Transfer to human agent"
            },
            "sms": {
                "url": "/exotel/applet/sms",
                "method": "POST",
                "description": "Send SMS confirmation"
            },
            "hangup": {
                "url": "/exotel/applet/hangup",
                "method": "POST",
                "description": "End call and save details"
            },
            "complete_flow": {
                "url": "/exotel/flow",
                "method": "POST",
                "description": "Single endpoint for all applets (use ?step=greeting/gather/etc)"
            }
        },
        "exotel_phone": settings.EXOTEL_PHONE_NUMBER,
        "base_url": "https://your-ngrok-url.ngrok.io"
    })
