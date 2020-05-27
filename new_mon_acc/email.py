from new_mon_acc import mail, app, celery
from flask_mail import Message


@celery.task
def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    with app.app_context():
        mail.send(msg)
