import os
from dotenv import load_dotenv
load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY','')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY','')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL','alerts@seudominio.com')
SMTP_HOST = os.getenv('SMTP_HOST','')
SMTP_PORT = int(os.getenv('SMTP_PORT','587'))
SMTP_USER = os.getenv('SMTP_USER','')
SMTP_PASS = os.getenv('SMTP_PASS','')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID','')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN','')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM','whatsapp:+14155238886')
WHATSAPP_TO = os.getenv('WHATSAPP_TO','whatsapp:+5561998611133')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL','leonardolopesesouza@gmail.com')
ADMIN_USER = os.getenv('ADMIN_USER','Leonardo Lopes de Souza')
MONTHS_BACK = int(os.getenv('MONTHS_BACK','6'))
STOCKS = [s.strip().upper() for s in os.getenv('STOCKS','AAPL,MSFT,TSLA,AMZN').split(',') if s.strip()]
CRYPTOS = [c.strip().lower() for c in os.getenv('CRYPTOS','bitcoin,ethereum').split(',') if c.strip()]
