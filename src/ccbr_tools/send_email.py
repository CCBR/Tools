#!/usr/bin/env python
"""
Send an email with an attachment
"""
from email.message import EmailMessage
import os
import smtplib


def send_email_msg(
    to_address="${USER}@hpc.nih.gov",
    text="This is an automated email",
    subject="test email from python",
    attach_html=None,
    from_addr="${USER}@hpc.nih.gov",
    debug=False,
):
    """
    Sends an email with an optional message & HTML attachment.

    Args:
        to_address (str): The email address of the recipient. Defaults to "${USER}@hpc.nih.gov".
        text (str, optional): The plain text content of the email. Defaults to None.
        subject (str): The subject line of the email. Defaults to "test email from python".
        attach_html (str, optional): The file path to the HTML attachment. Defaults to None.
        from_addr (str): The email address of the sender. Defaults to "${USER}@hpc.nih.gov".

    Raises:
        FileNotFoundError: If the HTML attachment file does not exist.
        smtplib.SMTPException: If there is an error sending the email.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_address

    if text:
        msg.set_content(text)
    if attach_html:
        with open(attach_html, "rb") as file:
            html_data = file.read()
        msg.add_attachment(
            html_data,
            filename=os.path.basename(attach_html),
            maintype="text",
            subtype="html",
        )
    if debug:
        return msg
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)