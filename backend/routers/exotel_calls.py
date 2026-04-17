"""
Exotel AI Calling Webhooks
Four main endpoints for handling voice calls with AI
"""
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import CallLog, CallRecording, Salon, Booking
from ai_voice_service import process_voice_input, clear_conversation, detect_intent
from exotel_client import exotel_client
from config import settings
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

router = APIRouter(tags=["Exotel AI Calling"])
logger = logging.getLogger(__name__)


def create_xml_response(message: str, action: str = "continue", gather_input: bool = True, 
                       redirect_url: str = None) -> str:
    """
    Create Exotel XML (TwiML-like) response.
    
    Args:
        message: Text to speak to caller
        action: 'continue', 'hangup', 'transfer', 'redirect'
        gather_input: Whether to collect next input
        redirect_url: URL to redirect call to (for transfers)
    """
    response = ET.Element("Response")
    
    # Add spoken message
    if message:
        say = ET.SubElement(response, "Say")
        say.set("voice", "woman")
        say.text = message
    
    # Handle different actions
    if action == "hangup":
        ET.SubElement(response, "Hangup")
        
    elif action == "transfer" and redirect_url:
        dial = ET.SubElement(response, "Dial")
        dial.text = redirect_url
        
    elif action == "redirect" and redirect_url:
        # Redirect to another flow
        redirect = ET.SubElement(response, "Redirect")
        redirect.set("method", "POST")
        redirect.text = redirect_url
        
    elif action == "gather" or (action == "continue" and gather_input):
        # Collect user input (speech or DTMF)
        gather = ET.SubElement(response, "Gather")
        gather.set("action", f"/exotel/gather")
        gather.set("method", "POST")
        gather.set("input", "speech dtmf")
        gather.set("speechTimeout", "auto")
        gather.set("numDigits", "1")
        gather.set("finishOnKey", "#")
        
        # Hint for user
        hint = ET.SubElement(gather, "Say")
        hint.text = "Please speak or press a key."
    
    return ET.tostring(response, encoding="unicode")


@router.post("/incoming")
async def incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(default="ringing"),
    db: Session = Depends(get_db)
):
    """
    Handle incoming calls from Exotel.
    Creates call log and returns welcome message.
    """
    try:
        logger.info(f"[Exotel] Incoming call from {From} to {To}, SID: {CallSid}")
        
        # Check for existing call log
        existing = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()
        if not existing:
            # Create new call log
            call_log = CallLog(
                call_sid=CallSid,
                from_number=From,
                to_number=To,
                direction="incoming",
                status=CallStatus
            )
            
            # Try to find customer by phone
            # Note: You might want to add a Customer model lookup here
            salon = db.query(Salon).filter(Salon.phone == To).first()
            if salon:
                call_log.salon_id = salon.id
            
            db.add(call_log)
            db.commit()
            logger.info(f"[Exotel] Created call log: {CallSid}")
        
        # Generate welcome message
        welcome_msg = "Hello! Welcome to BookSmart AI Salon. I'm your virtual assistant. How can I help you today?"
        
        # Return XML with gather to collect user input
        xml_response = create_xml_response(welcome_msg, "gather")
        
        return Response(content=xml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"[Exotel] Error in incoming call: {e}")
        error_xml = create_xml_response(
            "Sorry, we're experiencing technical difficulties. Please try again later.",
            "hangup"
        )
        return Response(content=error_xml, media_type="application/xml")


@router.post("/gather")
async def gather_input(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    Digits: str = Form(default=""),
    Confidence: float = Form(default=0.0),
    From: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Handle user input (speech or DTMF keypad).
    Processes with AI and returns response.
    """
    try:
        # Use speech if available, otherwise digits
        user_input = SpeechResult if SpeechResult else (Digits if Digits else "")
        
        logger.info(f"[Exotel] Gather input: '{user_input}' from {CallSid}, confidence: {Confidence}")
        
        if not user_input:
            # No input received
            xml_response = create_xml_response(
                "I didn't catch that. Could you please speak again?",
                "gather"
            )
            return Response(content=xml_response, media_type="application/xml")
        
        # Get call log for context
        call_log = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()
        
        # Build customer context
        customer_context = None
        if call_log and call_log.customer_name:
            customer_context = {"name": call_log.customer_name}
        
        # Process with AI
        ai_result = process_voice_input(CallSid, user_input, customer_context)
        
        # Update call log with transcript
        if call_log:
            if call_log.ai_transcript:
                call_log.ai_transcript += f"\nUser: {user_input}"
                call_log.ai_response += f"\nAI: {ai_result['message']}"
            else:
                call_log.ai_transcript = f"User: {user_input}"
                call_log.ai_response = f"AI: {ai_result['message']}"
            db.commit()
        
        # Handle different actions
        if ai_result["action"] == "hangup":
            # Clear conversation cache
            clear_conversation(CallSid)
            xml_response = create_xml_response(ai_result["message"], "hangup", gather_input=False)
            
        elif ai_result["action"] == "transfer":
            # Transfer to human agent
            xml_response = create_xml_response(
                ai_result["message"],
                "transfer",
                gather_input=False,
                redirect_url=settings.EXOTEL_PHONE_NUMBER  # Or support number
            )
            
        elif ai_result["action"] == "booking":
            # Booking flow - could redirect to specific booking handler
            xml_response = create_xml_response(ai_result["message"], "gather")
            
        else:
            # Continue conversation
            xml_response = create_xml_response(ai_result["message"], "gather")
        
        return Response(content=xml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"[Exotel] Error in gather: {e}")
        error_xml = create_xml_response(
            "Sorry, I didn't understand that. Could you try again?",
            "gather"
        )
        return Response(content=error_xml, media_type="application/xml")


@router.post("/status")
async def call_status(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(default=""),
    To: str = Form(default=""),
    Duration: str = Form(default="0"),
    RecordingUrl: str = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Handle call status updates from Exotel.
    Tracks call lifecycle: initiated → ringing → in-progress → completed/failed.
    """
    try:
        logger.info(f"[Exotel] Status update: {CallSid} is {CallStatus}")
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()
        
        if call_log:
            call_log.status = CallStatus.lower()
            
            if RecordingUrl:
                call_log.recording_url = RecordingUrl
            
            # Track timestamps
            if CallStatus == "in-progress":
                call_log.answered_at = datetime.utcnow()
            elif CallStatus in ["completed", "failed", "busy", "no-answer"]:
                call_log.ended_at = datetime.utcnow()
                # Clear conversation cache
                clear_conversation(CallSid)
            
            db.commit()
        else:
            logger.warning(f"[Exotel] Call log not found for {CallSid}")
        
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        logger.error(f"[Exotel] Error in status callback: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@router.post("/recording")
async def recording_callback(
    request: Request,
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(default="0"),
    db: Session = Depends(get_db)
):
    """
    Handle call recording callback from Exotel.
    Stores recording reference for future access.
    """
    try:
        logger.info(f"[Exotel] Recording received: {CallSid}, URL: {RecordingUrl}")
        
        # Update call log
        call_log = db.query(CallLog).filter(CallLog.call_sid == CallSid).first()
        
        if call_log:
            call_log.recording_url = RecordingUrl
            call_log.recording_duration = int(RecordingDuration) if RecordingDuration else 0
            db.commit()
            
            # Create separate recording record
            recording = CallRecording(
                call_id=call_log.id,
                recording_url=RecordingUrl,
                duration=int(RecordingDuration) if RecordingDuration else 0
            )
            db.add(recording)
            db.commit()
            
            logger.info(f"[Exotel] Saved recording for call {CallSid}")
        else:
            logger.warning(f"[Exotel] Call log not found for recording: {CallSid}")
        
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        logger.error(f"[Exotel] Error in recording callback: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


# ─── Outbound Call API ─────────────────────────────────────────────────────────

@router.post("/outbound")
async def make_outbound_call(
    phone_number: str,
    message: str = "Hi! This is BookSmart AI calling.",
    salon_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call to a customer.
    Requires Exotel credentials to be configured.
    """
    try:
        logger.info(f"[Exotel] Making outbound call to {phone_number}")
        
        # Use Exotel client to make call
        result = await exotel_client.make_call(
            to_number=phone_number,
            app_name=settings.EXOTEL_APP_ID
        )
        
        if result:
            # Create call log
            call_log = CallLog(
                call_sid=result.get("Call", {}).get("Sid", f"OUT{datetime.utcnow().timestamp()}"),
                from_number=settings.EXOTEL_PHONE_NUMBER,
                to_number=phone_number,
                direction="outgoing",
                status="initiated",
                salon_id=salon_id
            )
            db.add(call_log)
            db.commit()
            
            return JSONResponse(content={
                "status": "success",
                "call_sid": call_log.call_sid,
                "message": f"Call initiated to {phone_number}"
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to initiate call"
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"[Exotel] Outbound call error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


@router.post("/sms")
async def send_sms(
    phone_number: str,
    message: str,
    db: Session = Depends(get_db)
):
    """
    Send SMS via Exotel.
    """
    try:
        result = await exotel_client.send_sms(phone_number, message)
        
        if result:
            return JSONResponse(content={
                "status": "success",
                "message_sid": result.get("SMSMessage", {}).get("Sid")
            })
        else:
            return JSONResponse(content={
                "status": "error",
                "message": "Failed to send SMS"
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"[Exotel] SMS error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


# ─── Call Management APIs ──────────────────────────────────────────────────────

@router.get("/calls")
async def list_calls(
    limit: int = 50,
    offset: int = 0,
    salon_id: int = None,
    db: Session = Depends(get_db)
):
    """
    List call logs with pagination.
    """
    try:
        query = db.query(CallLog)
        if salon_id:
            query = query.filter(CallLog.salon_id == salon_id)
        
        calls = query.order_by(CallLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return JSONResponse(content={
            "status": "success",
            "calls": [
                {
                    "id": c.id,
                    "call_sid": c.call_sid,
                    "from_number": c.from_number,
                    "to_number": c.to_number,
                    "direction": c.direction,
                    "status": c.status,
                    "customer_name": c.customer_name,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "ended_at": c.ended_at.isoformat() if c.ended_at else None,
                    "recording_url": c.recording_url,
                    "ai_transcript": c.ai_transcript[:200] + "..." if c.ai_transcript and len(c.ai_transcript) > 200 else c.ai_transcript
                }
                for c in calls
            ],
            "total": query.count()
        })
        
    except Exception as e:
        logger.error(f"[Exotel] List calls error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


@router.get("/calls/{call_sid}")
async def get_call_details(
    call_sid: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific call.
    """
    try:
        call = db.query(CallLog).filter(CallLog.call_sid == call_sid).first()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return JSONResponse(content={
            "status": "success",
            "call": {
                "id": call.id,
                "call_sid": call.call_sid,
                "from_number": call.from_number,
                "to_number": call.to_number,
                "direction": call.direction,
                "status": call.status,
                "customer_name": call.customer_name,
                "salon_id": call.salon_id,
                "created_at": call.created_at.isoformat() if call.created_at else None,
                "answered_at": call.answered_at.isoformat() if call.answered_at else None,
                "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                "recording_url": call.recording_url,
                "recording_duration": call.recording_duration,
                "ai_transcript": call.ai_transcript,
                "ai_response": call.ai_response
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Exotel] Get call error: {e}")
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


@router.get("/config")
async def get_config():
    """
    Get Exotel configuration for frontend/setup.
    """
    return JSONResponse(content={
        "status": "success",
        "config": {
            "exotel_number": settings.EXOTEL_PHONE_NUMBER,
            "webhook_urls": {
                "incoming": "/exotel/incoming",
                "gather": "/exotel/gather",
                "status": "/exotel/status",
                "recording": "/exotel/recording"
            },
            "mock_mode": exotel_client.mock_mode
        }
    })
