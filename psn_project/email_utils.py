from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
from django.core.mail import get_connection

logger = logging.getLogger(__name__)

# Email configuration mapping
EMAIL_CONFIG = {
    'AIS140': {
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_USE_SSL': False,
        'EMAIL_HOST_USER': 'ais140danlaw@danlawtechnologies.com',
        'EMAIL_HOST_PASSWORD': 'sumj ytxh buxf fpra',
        'DEFAULT_FROM_EMAIL': 'ais140danlaw@danlawtechnologies.com',
    },
    'default': {
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': settings.EMAIL_PORT,
        'EMAIL_USE_SSL': settings.EMAIL_USE_SSL,
        'EMAIL_USE_TLS': False,
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
        'EMAIL_HOST_PASSWORD': settings.EMAIL_HOST_PASSWORD,
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
}
AIS140_SENDER = 'ais140danlawtech@danlawtechnologies.com'
AIS140_RECIPIENTS = ['sales@danlawtech.com', 'upendram@danlawtech.com']
def send_email_with_config(subject, html_message, recipient_list, cc_list=None, attachments=None, config_type='default'):
    """
    Send email with HTML content and optional attachments.
    
    Args:
        subject: Email subject line
        html_message: HTML content of the email
        recipient_list: List of recipient email addresses
        cc_list: List of CC email addresses (optional)
        attachments: List of file paths to attach (optional)
        config_type: Email configuration type (e.g., 'AIS140' or 'default')
    
    Returns:
        Number of emails sent
    """
    try:
        if not recipient_list:
            logger.warning(f"No recipients provided for email: {subject}")
            return 0
        if isinstance(recipient_list, str):
            recipient_list = [recipient_list]
        recipient_list = [e.strip() for e in recipient_list if e and isinstance(e, str)]
        if not recipient_list:
            logger.warning(f"No valid recipients after filtering for email: {subject}")
            return 0

        if cc_list:
            if isinstance(cc_list, str):
                cc_list = [cc_list]
            cc_list = [e.strip() for e in cc_list if e and isinstance(e, str)]
        else:
            cc_list = []

        config = EMAIL_CONFIG.get(config_type, EMAIL_CONFIG['default'])
        from_email = config.get('DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=config.get('EMAIL_HOST'),
            port=config.get('EMAIL_PORT'),
            username=config.get('EMAIL_HOST_USER'),
            password=config.get('EMAIL_HOST_PASSWORD'),
            use_tls=config.get('EMAIL_USE_TLS', False),
            use_ssl=config.get('EMAIL_USE_SSL', False),
        )

        # Use the custom connection
        email = EmailMultiAlternatives(
            subject=subject,
            body="",  # plain-text fallback (empty or provide plain text)
            from_email=from_email,
            to=recipient_list,
            cc=cc_list,
            connection=connection,
        )

        # Attach HTML alternative
        if html_message:
            email.attach_alternative(html_message, "text/html")

        # Attachments: accept tuples (filename, content, mime), FileField-like objects, or file paths
        if attachments:
            import os
            for att in attachments:
                try:
                    if isinstance(att, (list, tuple)) and len(att) >= 2:
                        filename = att[0]
                        content = att[1]
                        mime = att[2] if len(att) > 2 else None
                        if mime:
                            email.attach(filename, content, mime)
                        else:
                            email.attach(filename, content)
                    elif hasattr(att, 'read') and hasattr(att, 'name'):
                        # Django FileField or file-like
                        content = att.read()
                        filename = os.path.basename(getattr(att, 'name') or '')
                        email.attach(filename, content)
                    elif isinstance(att, str) and os.path.exists(att):
                        # filesystem path
                        with open(att, 'rb') as f:
                            content = f.read()
                        filename = os.path.basename(att)
                        email.attach(filename, content)
                    else:
                        logger.warning(f"Skipping unknown attachment format: {type(att)}")
                except Exception as e:
                    logger.error(f"Error attaching file {att}: {e}")

        email.send()
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False