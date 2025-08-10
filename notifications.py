
import os, smtplib
from email.mime.text import MIMEText

def send_email(to_list, subject, body):
    host = os.getenv('SMTP_HOST'); port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER'); password = os.getenv('SMTP_PASS'); sender = os.getenv('SMTP_FROM', user)
    if not host or not user or not password:
        print('[email] SMTP não configurado. Pulei envio.')
        return False
    if isinstance(to_list, str): to_list = [e.strip() for e in to_list.split(';') if e.strip()]
    msg = MIMEText(body, 'plain', 'utf-8'); msg['Subject']=subject; msg['From']=sender; msg['To']=', '.join(to_list)
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls(); smtp.login(user, password); smtp.sendmail(sender, to_list, msg.as_string())
    print(f'[email] Enviado para {to_list}'); return True

def send_whatsapp(to_list, text):
    provider = os.getenv('WHATSAPP_PROVIDER', '').lower()
    if isinstance(to_list, str): to_list = [e.strip() for e in to_list.split(';') if e.strip()]
    if not provider:
        print('[whatsapp] Provedor não configurado. Pulei envio.'); return False
    if provider == 'twilio':
        from twilio.rest import Client
        sid = os.getenv('TWILIO_SID'); token = os.getenv('TWILIO_TOKEN'); from_num = os.getenv('TWILIO_FROM')  # ex: whatsapp:+14155238886
        if not sid or not token or not from_num:
            print('[whatsapp] Twilio não configurado.'); return False
        cli = Client(sid, token)
        for to in to_list:
            if not to.startswith('whatsapp:'): to = 'whatsapp:' + to
            cli.messages.create(body=text, from_=from_num, to=to)
        print(f'[whatsapp] Enviado para {to_list}'); return True
    print('[whatsapp] Provedor não suportado.'); return False
