from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from egg_timer import settings


def send_email(recipient, subject, text_body, html_body):
    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    smtp.starttls()
    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    msg = MIMEMultipart(text_body)
    msg['Subject'] = subject
    msg['From'] = settings.FROM_EMAIL
    msg['To'] = recipient

    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    smtp.sendmail(settings.FROM_EMAIL, [recipient], msg.as_string())
    smtp.quit()