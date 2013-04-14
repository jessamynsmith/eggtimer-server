from django.core.mail import EmailMultiAlternatives


def send(recipient, subject, text_body, html_body):
    recipients = [(recipient.full_name, recipient.email)]
    msg = EmailMultiAlternatives(subject, text_body, to=recipients)
    msg.attach_alternative(html_body, "text/html")
    msg.send()