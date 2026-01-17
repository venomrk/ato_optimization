#!/bin/bash

echo "🚀 Starting Unified Research & Chemistry Platform"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found"
    echo "Please install docker-compose"
    exit 1
fi

echo "✅ docker-compose found"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down > /dev/null 2>&1

echo "📦 Building and starting services..."
echo ""

# Start services
docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: Services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "✅ All services are running!"
echo ""
echo "=================================================="
echo "🌐 ACCESS THE PLATFORM"
echo "=================================================="
echo ""
echo "🎨 Frontend:      http://localhost:3001"
echo "🔧 Backend API:   http://localhost:8080"
echo "📚 API Docs:      http://localhost:8080/docs"
echo ""
echo "=================================================="
echo "📖 QUICK START GUIDE"
echo "=================================================="
echo ""
echo "1. Open http://localhost:3001 in your browser"
echo "2. Click 'Register' to create an account"
echo "3. You'll get 100 free credits to start"
echo "4. Go to Settings to configure OpenRouter API key"
echo "5. Try the Research or Chemistry tabs"
echo ""
echo "=================================================="
echo "💡 DEMO CREDENTIALS (Optional)"
echo "=================================================="
echo ""
echo "You can create your own account, or use:"
echo "Email: demo@example.com"
echo "Password: demo123"
echo "(Create this account on first login)"
echo ""
echo "=================================================="
echo "🛠️  USEFUL COMMANDS"
echo "=================================================="
echo ""
echo "View logs:        docker-compose logs -f"
echo "Stop services:    docker-compose down"
echo "Restart:          docker-compose restart"
echo ""
echo "=================================================="
echo ""
echo "✨ Platform is ready! Opening browser..."
echo ""

# Try to open browser (works on Linux with xdg-open, macOS with open)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3001 &> /dev/null &
elif command -v open &> /dev/null; then
    open http://localhost:3001 &> /dev/null &
else
    echo "Please open http://localhost:3001 manually in your browser"
fi

echo "🎉 Enjoy the platform!"
echo ""

# Show live logs
echo "📊 Showing live logs (Ctrl+C to exit)..."
echo ""
docker-compose logs -f
