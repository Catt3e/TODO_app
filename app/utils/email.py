import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings


async def send_verification_email(email_to: str, code: str):

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_USER
    msg["To"] = email_to
    msg["Subject"] = "Verify your email for To-Do List"

    html = f"""
    <h2>Welcome to the To-Do List app!</h2>
    <p>This is your verification code:</p>
    <h1>{code}</h1>
    <p>The code expires in {settings.VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>
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
