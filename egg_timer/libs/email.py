import sendgrid

from egg_timer import settings


def send_email(recipient, subject, text_body, html_body):
    email = sendgrid.Sendgrid(settings.EMAIL_HOST_USER,
                              settings.EMAIL_HOST_PASSWORD, secure=True)

    message = email.Message(settings.FROM_EMAIL, subject, text_body,
                            html_body)
    message.add_to(recipient.email, recipient.full_name)

    email.smtp.send(message)
