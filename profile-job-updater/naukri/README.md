# Naukri Auto-Refresh — Live Setup

These are the actual scripts running in production on the AWS Mumbai VM.

## Files
- **`daily_refresh.py`** — Python script: login via NopeRi HTTP API → re-save headline → log → email on failure
- **`run_refresh.sh`** — bash wrapper that cron invokes (activates venv, runs python, appends to log)

## Where they live on the VM
```
ubuntu@<aws-mumbai-ip>:~/NopeRi/
├── daily_refresh.py        ← this file
├── run_refresh.sh          ← wrapper
├── .env                    ← credentials (NEVER commit)
├── refresh.log             ← python logs
├── cron.log                ← cron wrapper logs
└── src/                    ← NopeRi library (cloned from Traverser25/NopeRi)
```

## Cron schedule (IST)
```
20 9  * * *   → 09:20 AM
40 14 * * *   → 02:40 PM
30 19 * * *   → 07:30 PM
```
Plus 0-180s random jitter inside the script itself.

## Secrets expected in `.env`
```
USERNAME=<naukri email>
PASSWORD=<naukri password>
GMAIL_APP_PASSWORD=<16-char gmail app password>
NOTIFY_EMAIL=<where failure alerts go>
HEADLINE=<optional — override default headline>
```
