import datetime
import smtplib  

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


from itsdangerous import URLSafeTimedSerializer

from settings import (salt_code, SECRET, BASE_URL, 
                        SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD,
                        SMTP_FROM_ADDRESS)
from tasks.config import huey

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET)
    return serializer.dumps(email, salt=salt_code)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET)
    try:
        email = serializer.loads(
            token,
            salt=salt_code,
            max_age=expiration
        )
    except:
        return False
    return email

def send_email_by_smtp(from_, to, body):
    ''' sends a mime message to mailgun SMTP gateway '''
    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.login(SMTP_LOGIN, SMTP_PASSWORD)
    smtp.sendmail(from_, to, body)
    smtp.quit()    

@huey.task()
def send_activation_email(profile):

    receiver = profile.user.email
    url = f'{BASE_URL}/registration/active/{generate_confirmation_token(receiver)}'

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Email confirmation'
    msgRoot['From'] = SMTP_FROM_ADDRESS
    msgRoot['To'] = receiver
    msgRoot.preamble = 'Verify your email'

    
    message = f'Please validate your email by clicking here {url}'

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgAlternative.attach(MIMEText(message))
    send_email_by_smtp(SMTP_FROM_ADDRESS, receiver, msgRoot.as_string())
    profile.user.confirmation_sent_at = datetime.datetime.now()
    profile.user.save()