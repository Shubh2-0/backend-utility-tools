'''Daily Naukri profile refresh via NopeRi HTTP API.

Refreshes 'lastModified' timestamp so profile appears in recruiter's
'Active today' filter. Does NOT change any visible content.

Sends email notification via Gmail SMTP if the run fails.
'''
import logging
import os
import random
import smtplib
import socket
import ssl
import sys
import time
import traceback
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv
from src.client.naukri_client import NaukriLoginClient

load_dotenv()

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'refresh.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger('refresh')

HEADLINE = os.getenv('HEADLINE') or (
    'Java Backend Engineer | 3 Yrs | Spring Boot · Microservices · AWS · '
    'Docker · MySQL · RabbitMQ | Built Production Systems for 10+ '
    'Enterprise Clients | Immediate Joiner'
)


def send_failure_email(stage: str, error: str) -> None:
    '''Send failure notification via Gmail SMTP. Silent if credentials absent.'''
    gmail_user = os.getenv('USERNAME')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient = os.getenv('NOTIFY_EMAIL') or gmail_user
    if not (gmail_user and app_password and recipient):
        log.warning('Email creds missing; skipping notification')
        return

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
    host = socket.gethostname()

    msg = EmailMessage()
    msg['Subject'] = f'Naukri auto-refresh FAILED — {stage}'
    msg['From'] = gmail_user
    msg['To'] = recipient
    msg.set_content(
        f'''Naukri profile auto-refresh failed.

Time:    {ts}
Host:    {host}
Stage:   {stage}

Error:
{error}

---
This is an automated alert from your Naukri auto-refresh tool
running on AWS Mumbai EC2. Check the log:
  ssh ubuntu@{host} 'tail -50 /home/ubuntu/NopeRi/cron.log'

If this keeps failing, most likely causes:
 1. Naukri password changed — update .env file on the VM
 2. Naukri account locked — log in manually once to unlock
 3. VM lost internet — check EC2 console

Recent log:
{tail_log()}
'''
    )

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=ctx)
            smtp.login(gmail_user, app_password)
            smtp.send_message(msg)
        log.info('Failure email sent to %s', recipient)
    except Exception as e:
        log.error('Could not send failure email: %s', e)


def tail_log(lines: int = 15) -> str:
    try:
        with open(LOG_FILE, 'r') as f:
            return ''.join(f.readlines()[-lines:])
    except Exception:
        return '(no log)'


def main() -> int:
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    if not username or not password:
        err = 'USERNAME/PASSWORD missing in .env'
        log.error(err)
        send_failure_email('config', err)
        return 1

    jitter = random.randint(0, 180)
    log.info('=== Daily Refresh Run === (jitter %ds)', jitter)
    time.sleep(jitter)

    # --- Login stage ---
    try:
        client = NaukriLoginClient(username, password)
        client.login()
        log.info('Login OK for %s', username)
    except Exception as e:
        err = f'{type(e).__name__}: {e}'
        log.error('Login failed: %s', err)
        log.error(traceback.format_exc())
        send_failure_email('login', err + '\n\n' + traceback.format_exc())
        return 2

    # --- Update stage ---
    try:
        result = client.update_profile(headline=HEADLINE)
        log.info('Profile refreshed. Status=%s ProfileID=%s',
                 result.status_code, result.profile_id)
        log.info('=== Run completed successfully ===')
        return 0
    except Exception as e:
        err = f'{type(e).__name__}: {e}'
        log.error('Update failed: %s', err)
        log.error(traceback.format_exc())
        send_failure_email('update', err + '\n\n' + traceback.format_exc())
        return 3


if __name__ == '__main__':
    sys.exit(main())
