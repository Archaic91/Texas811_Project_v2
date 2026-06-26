import smtplib
from email.message import EmailMessage
import os


# =====================================================
# EMAIL SENDER (SINGLE RESPONSIBILITY)
# =====================================================

def send_email_with_attachments(
    recipients,
    subject,
    body,
    file_paths,
    sender_email,
    sender_password,
    smtp_server="smtp.gmail.com",
    smtp_port=587
):

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.set_content(body)

    # Attach files safely
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(file_path)
                )

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent successfully")
