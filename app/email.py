from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail
import sys

def send_async_email(app, msg):
    with app.app_context():
        print(current_app.config, file=sys.stderr)
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if sync:
        mail.send(msg)
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()