"""
Email Templates for BookSmart AI
Rich HTML email templates for various notifications
"""
from typing import Optional
from datetime import datetime

class EmailTemplates:
    """HTML Email Templates"""
    
    @staticmethod
    def booking_confirmation(customer_name: str, service: str, date: str, time: str, 
                           booking_ref: str, salon_name: str = "BookSmart AI Salon") -> tuple:
        """Booking confirmation email"""
        subject = f"✅ Booking Confirmed - {service}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #2C3E35, #4A7C59); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .booking-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ display: flex; margin: 10px 0; }}
                .detail-label {{ font-weight: bold; width: 120px; color: #555; }}
                .detail-value {{ color: #333; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
                .cta-button {{ display: inline-block; background: #2C3E35; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 25px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Booking Confirmed!</h1>
                    <p>Thank you for choosing {salon_name}</p>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    <p>Your appointment has been successfully booked. Here are your booking details:</p>
                    
                    <div class="booking-details">
                        <div class="detail-row">
                            <span class="detail-label">Service:</span>
                            <span class="detail-value">{service}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span class="detail-value">{date}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span class="detail-value">{time}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Reference:</span>
                            <span class="detail-value" style="font-family: monospace; background: #e9ecef; padding: 2px 8px; border-radius: 4px;">{booking_ref}</span>
                        </div>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="#" class="cta-button">Manage Booking</a>
                    </p>
                    
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        Need to reschedule? Reply to this email or call us at 9513886363.
                    </p>
                </div>
                <div class="footer">
                    <p>{salon_name} | AI-Powered Salon Management</p>
                    <p>© {datetime.now().year} BookSmart AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
Hi {customer_name},

Your booking is confirmed!

Service: {service}
Date: {date}
Time: {time}
Reference: {booking_ref}

Thank you for choosing {salon_name}.

Need to reschedule? Call us at 9513886363.
"""
        
        return subject, html, text
    
    @staticmethod
    def appointment_reminder(customer_name: str, service: str, date: str, time: str,
                           salon_address: str = "BookSmart AI Salon") -> tuple:
        """Appointment reminder email"""
        subject = f"⏰ Reminder: {service} Appointment Tomorrow"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #FF9800, #F57C00); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; }}
                .reminder-box {{ background: #FFF3E0; padding: 20px; border-left: 4px solid #FF9800; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Appointment Reminder</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    
                    <div class="reminder-box">
                        <h3>Tomorrow's Appointment</h3>
                        <p><strong>Service:</strong> {service}</p>
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Time:</strong> {time}</p>
                        <p><strong>Location:</strong> {salon_address}</p>
                    </div>
                    
                    <p>We're looking forward to seeing you!</p>
                    <p style="font-size: 14px; color: #666;">
                        Running late? Call us at 9513886363.
                    </p>
                </div>
                <div class="footer">
                    <p>BookSmart AI | Smart Salon Management</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
Hi {customer_name},

REMINDER: You have an appointment tomorrow!

Service: {service}
Date: {date}
Time: {time}
Location: {salon_address}

We're looking forward to seeing you!

Running late? Call us at 9513886363.
"""
        
        return subject, html, text
    
    @staticmethod
    def promotional_offer(customer_name: str, offer_title: str, offer_details: str,
                         valid_until: str, discount_code: str) -> tuple:
        """Promotional offer email"""
        subject = f"🎉 {offer_title}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #E91E63, #C2185B); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; text-align: center; }}
                .offer-box {{ background: #FCE4EC; padding: 30px; border-radius: 10px; margin: 20px 0; }}
                .discount-code {{ background: #2C3E35; color: white; padding: 15px 30px; font-size: 24px; 
                                 font-weight: bold; letter-spacing: 2px; border-radius: 8px; display: inline-block; margin: 20px 0; }}
                .cta-button {{ display: inline-block; background: #E91E63; color: white; padding: 15px 40px; 
                              text-decoration: none; border-radius: 30px; font-size: 18px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Special Offer Just For You!</h1>
                </div>
                <div class="content">
                    <p>Hi {customer_name},</p>
                    
                    <div class="offer-box">
                        <h2>{offer_title}</h2>
                        <p>{offer_details}</p>
                        <p style="color: #C2185B; font-weight: bold;">Valid until: {valid_until}</p>
                        
                        <div class="discount-code">{discount_code}</div>
                        
                        <p style="font-size: 14px; color: #666;">Use this code at checkout</p>
                    </div>
                    
                    <a href="#" class="cta-button">Book Now</a>
                    
                    <p style="margin-top: 30px; font-size: 12px; color: #888;">
                        Terms and conditions apply. Cannot be combined with other offers.
                    </p>
                </div>
                <div class="footer">
                    <p>BookSmart AI | Smart Salon Management</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text = f"""
Hi {customer_name},

🎉 Special Offer Just For You!

{offer_title}
{offer_details}

Use code: {discount_code}
Valid until: {valid_until}

Book now and save!

Terms and conditions apply.
"""
        
        return subject, html, text
