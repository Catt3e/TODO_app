import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_verification_email(email_to: str, token: str):
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"  # ← change to your frontend URL later

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_USER
    msg["To"] = email_to
    msg["Subject"] = "Verify your email for To-Do List"

    html = f"""
    <h2>Welcome to the To-Do List app!</h2>
    <p>Click the link below to verify your email:</p>
    <a href="{verification_link}">Verify Email</a>
    <p>The link expires in {settings.VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>
    """
    msg.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_USER,
        password=settings.EMAIL_PASSWORD,
        start_tls=True,
    )