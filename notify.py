import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient
from .config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, ADMIN_EMAIL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO
logger = logging.getLogger('notify')
def format_text_report(suggestions):
    lines = ['Invest Bot — Daily Recommendations','\nDaily:']
    for r in suggestions.get('daily',[]):
        lines.append(f"{r.get('symbol')} ({r.get('asset_type')}): {r.get('recommendation')} — risk {r.get('risk_score')}")
    return '\n'.join(lines)
def send_email(subject, plain_text, html_content=None, to_email=ADMIN_EMAIL):
    if SENDGRID_API_KEY and SENDGRID_FROM_EMAIL:
        try:
            message = Mail(from_email=SENDGRID_FROM_EMAIL, to_emails=to_email, subject=subject, plain_text_content=plain_text, html_content=html_content)
            sg = SendGridAPIClient(SENDGRID_API_KEY); res = sg.send(message); logger.info('SendGrid status %s', res.status_code); return True
        except Exception as e:
            logger.exception('SendGrid error %s', e)
    return False
def send_whatsapp(message, to=WHATSAPP_TO):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM and to): return False
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(body=message, from_=TWILIO_WHATSAPP_FROM, to=to); logger.info('Twilio SID %s', msg.sid); return True
    except Exception as e:
        logger.exception('Twilio error %s', e); return False
