import os
import smtplib
from email.message import EmailMessage
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try getting from Streamlit Secrets first, fallback to os.environ (local)
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

SMTP_PASSWORD = get_secret("SMTP_PASSWORD") or get_secret("SENDGRID_API_KEY")
SENDER_EMAIL = get_secret("SENDER_EMAIL")

if SMTP_PASSWORD:
    # Google App Passwords often have spaces when copied, remove them
    SMTP_PASSWORD = SMTP_PASSWORD.replace(" ", "")

def send_otp_email(receiver_email, otp):
    if not SMTP_PASSWORD or not SENDER_EMAIL:
        raise Exception("Google App Password or Sender Email missing from secrets!")
        
    msg = EmailMessage()
    msg.set_content(f"Hello!\\n\\nYour secure FitPlan AI OTP is: {otp}\\n\\nWelcome to the platform.")
    msg["Subject"] = "Your FitPlan AI OTP"
    msg["From"] = f"FitPlan AI <{SENDER_EMAIL}>"
    msg["To"] = receiver_email

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise Exception("Gmail Authentication Failed. Check your 16-letter App Password!")
    except Exception as e:
        raise Exception(f"Failed to send email via Gmail: {str(e)}")
