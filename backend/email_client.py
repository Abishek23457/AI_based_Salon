"""
Email notification client for BookSmart AI.
Uses SMTP (Gmail-compatible) to send booking confirmations and reminders.
Falls back to console print when credentials are not configured.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings


def send_booking_email(
    to_email: str,
    customer_name: str,
    service_name: str,
    appointment_time: str,
    salon_name: str = "BookSmart AI Salon",
    subject_prefix: str = "Booking Confirmed",
):
    """Send a styled booking confirmation or reminder email."""
    smtp_user = settings.SMTP_EMAIL
    smtp_pass = settings.SMTP_PASSWORD

    if not smtp_user or not smtp_pass:
        print(f"[Email] SMTP not configured. Mock email to {to_email}: {subject_prefix} — {service_name} at {appointment_time}")
        return None

    subject = f"{subject_prefix} — {service_name} | {salon_name}"

    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width:520px; margin:0 auto; border:1px solid #e5e7eb; border-radius:16px; overflow:hidden;">
        <div style="background:#2C3E35; padding:28px 32px;">
            <h1 style="color:#fff; margin:0; font-size:22px; letter-spacing:1px;">{salon_name}</h1>
        </div>
        <div style="padding:32px;">
            <p style="font-size:16px; color:#1A2520;">Hi <strong>{customer_name}</strong>,</p>
            <p style="font-size:15px; color:#444; line-height:1.7;">
                Your <strong>{service_name}</strong> appointment has been <strong style="color:#2C3E35;">{subject_prefix.lower()}</strong>!
            </p>
            <div style="background:#f9fafb; border-radius:12px; padding:20px; margin:20px 0; border:1px solid #e5e7eb;">
                <p style="margin:0 0 8px; font-size:13px; color:#888; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Appointment Details</p>
                <p style="margin:4px 0; font-size:15px;"><strong>Service:</strong> {service_name}</p>
                <p style="margin:4px 0; font-size:15px;"><strong>Date & Time:</strong> {appointment_time}</p>
            </div>
            <p style="font-size:13px; color:#999; margin-top:24px;">
                Need to reschedule? Reply to this email or call us directly.<br/>
                Cancellation policy: 24-hour notice required.
            </p>
        </div>
        <div style="background:#f3f4f6; padding:16px 32px; text-align:center;">
            <p style="margin:0; font-size:12px; color:#aaa;">© 2026 {salon_name} • Powered by BookSmart AI</p>
        </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(f"{subject_prefix}: {service_name} on {appointment_time} for {customer_name}", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[Email] Sent {subject_prefix} email to {to_email}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send to {to_email}: {e}")
        return None
