#!/bin/bash
# Start Celery workers and beat scheduler for local development

echo "Starting Celery workers... Ensure Redis is running."

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   brew services start redis  # macOS"
    echo "   sudo systemctl start redis  # Linux"
    echo "   docker run -d -p 6379:6379 redis:7-alpine  # Docker"
    exit 1
fi

echo "✅ Redis is running"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start a worker for the main queues
echo "Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 --queues=evidence,compliance,notifications,reports -E --logfile=logs/celery_worker.log &
WORKER_PID=$!

# Start the Celery Beat scheduler for periodic tasks
echo "Starting Celery Beat scheduler..."
celery -A celery_app beat --loglevel=info --pidfile=/tmp/celerybeat.pid --logfile=logs/celery_beat.log &
BEAT_PID=$!

# Start Flower for monitoring (optional)
if command -v flower &> /dev/null; then
    echo "Starting Flower monitoring..."
    celery -A celery_app flower --port=5555 --logfile=logs/flower.log &
    FLOWER_PID=$!
    echo "📊 Flower monitoring available at http://localhost:5555"
fi

echo "🚀 Celery workers and beat scheduler started."
echo "📋 Worker PID: $WORKER_PID"
echo "⏰ Beat PID: $BEAT_PID"
echo "📁 Logs available in ./logs/ directory"
echo ""
echo "To stop all processes:"
echo "   pkill -f celery"
echo "   or use: kill $WORKER_PID $BEAT_PID"
echo ""
echo "To monitor tasks:"
echo "   celery -A celery_app inspect active"
echo "   celery -A celery_app inspect scheduled"

# Wait for any process to exit
wait