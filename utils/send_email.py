from django.core.mail import send_mail
from django.conf import settings

def send_email(subject: str, email: str, message: str):
    error_message = None
    try:
        from_email = settings.EMAIL_HOST_USER
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
        )
        return True, error_message
    except Exception as e:
        error_message = str(e)
        return False, error_message