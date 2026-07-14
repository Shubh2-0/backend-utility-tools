#!/bin/bash
# One-shot deploy script — paste into AWS EC2 Instance Connect terminal
# Sets up Java job alert bot on Mumbai VM. Idempotent — safe to re-run.

set -e

BOT_DIR="$HOME/naukri-alert-bot"
NOPERI_DIR="$HOME/NopeRi"

echo "==> Creating bot directory"
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

echo "==> Pulling latest NopeRi (with search_jobs feature)"
if [ -d "$NOPERI_DIR/.git" ]; then
    cd "$NOPERI_DIR"
    git pull --rebase || git fetch && git reset --hard origin/main
    cd "$BOT_DIR"
else
    git clone https://github.com/Traverser25/NopeRi.git "$NOPERI_DIR"
fi

echo "==> Installing dependencies"
source "$NOPERI_DIR/venv/bin/activate" 2>/dev/null || {
    python3 -m venv "$NOPERI_DIR/venv"
    source "$NOPERI_DIR/venv/bin/activate"
}
pip install -q --upgrade pip
pip install -q -r "$NOPERI_DIR/requirements.txt"
pip install -q python-dotenv requests pycryptodome colorama

echo "==> Adding cron entry (every 10 min)"
CRON_LINE="*/10 * * * * /bin/bash $BOT_DIR/run_alert.sh"
( crontab -l 2>/dev/null | grep -vF "$BOT_DIR/run_alert.sh" ; echo "$CRON_LINE" ) | crontab -

echo ""
echo "==> Setup complete"
echo ""
echo "Next steps:"
echo "  1. Edit env: nano $BOT_DIR/.env  (paste WHATSAPP_PHONE + CALLMEBOT_API_KEY)"
echo "  2. Test once: bash $BOT_DIR/run_alert.sh"
echo "  3. Watch log: tail -f $BOT_DIR/cron.log"
echo ""
echo "Cron will fire every 10 min from now on."
