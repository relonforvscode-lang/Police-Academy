#!/bin/bash
# Build script for Render deployment

echo "======================================"
echo "🚀 Building Django Application"
echo "======================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
# If DATABASE_URL is Postgres (Render), install Render-friendly requirements without mysqlclient
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -qi "postgres"; then
	echo "Detected PostgreSQL DATABASE_URL — installing requirements-render.txt"
	pip install -r requirements-render.txt
else
	pip install -r requirements.txt
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional for Render)
# python manage.py shell < scripts/create_admin.py

echo "======================================"
echo "✅ Build completed successfully!"
echo "======================================"
