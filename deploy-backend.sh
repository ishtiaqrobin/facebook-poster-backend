#!/bin/bash

# ----- Configuration -----
LOCAL_PROJECT_PATH="/mnt/e/MIssion404/Python/Facebook/facebook_backend/"
REMOTE_USER="ezbitlyc"
REMOTE_HOST="facebook-poster-backend.ezbitly.com"
REMOTE_PROJECT_PATH="/home/ezbitlyc/facebook-poster-backend.ezbitly.com"
VENV_ACTIVATE_PATH="/home/ezbitlyc/virtualenv/facebook-poster-backend.ezbitly.com/3.11/bin/activate"

# ----- Telegram Setup -----
TELEGRAM_BOT_TOKEN="8088105192:AAGxfLWgNHJJAZKuyLqnuks5x0m20PClLPg"
TELEGRAM_CHAT_ID="-1002596853653"

send_telegram() {
  MESSAGE="$1"
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    -d text="$MESSAGE" \
    -d parse_mode="Markdown"
}

send_telegram "🚀 *Facebook Poster Backend Deployment Started!*"

# Step 1: Upload project via rsync (excluding venv, .git, etc.)
echo "📤 Uploading Facebook Poster Backend project..."
if rsync -avz --delete "$LOCAL_PROJECT_PATH" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PROJECT_PATH" \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude 'staticfiles' \
  --exclude 'passenger_wsgi.py' \
  --exclude '.htaccess'; then
  send_telegram "✅ *Facebook Poster Backend Project Uploaded Successfully!*"
else
  send_telegram "❌ *Facebook Poster Backend Project Upload Failed!*"
  exit 1
fi

# Step 2: SSH into server to run Django commands
ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
  cd "$REMOTE_PROJECT_PATH"
  source "$VENV_ACTIVATE_PATH"

  # Install dependencies
  pip install -r requirements.txt

  # Run migrations
  python manage.py migrate

  # Collect static files
  python manage.py collectstatic --noinput

  # Restart passenger
  #   mkdir -p tmp
  #   touch tmp/restart.txt

  # Restart passenger properly
  echo "♻️ Facebook Poster Backend Passenger app Restarting..."
  mkdir -p tmp
  echo $(date) > tmp/restart.txt
  touch passenger_wsgi.py
  echo "✅ Facebook Poster Backend app restarted successfully!"

EOF

if [ $? -eq 0 ]; then
  send_telegram "♻️ *Facebook Poster Backend Server Restarted Successfully!*"
else
  send_error "❌ Facebook Poster Backend Server restart failed!"
  exit 1
fi

# Step 3: Deployment Complete
echo "🏁 Facebook Poster Backend Deployment Completed Successfully!"
send_telegram "🏁 *Facebook Poster Backend Deployment Completed Successfully!*\n🔗 Visit: http://$REMOTE_HOST"

# Save deployment log
echo "📅 Facebook Poster Backend Deployment date: $(date)" >> deployment.log
echo "🚀 Facebook Poster Backend Deployment Completed Successfully!" >> deployment.log
