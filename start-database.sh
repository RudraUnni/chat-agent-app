#!/bin/bash

# Start Database Services Script
echo "🐘 Starting PostgreSQL and pgAdmin in Docker..."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "🔄 Starting database services..."
echo "   PostgreSQL will be available at: localhost:5432"
echo "   pgAdmin will be available at: http://localhost:5050"
echo ""

# Start only the database services
docker-compose up -d postgres

# Check if user wants pgAdmin
read -p "🤔 Do you want to start pgAdmin as well? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Starting pgAdmin..."
    docker-compose --profile dev up -d pgadmin
    echo ""
    echo "✅ Database services started successfully!"
    echo ""
    echo "📊 pgAdmin Access:"
    echo "   URL: http://localhost:5050"
    echo "   Email: admin@chatapp.local"
    echo "   Password: admin_password"
    echo ""
    echo "🔗 To connect to PostgreSQL from pgAdmin:"
    echo "   Host: localhost (or host.docker.internal on some systems)"
    echo "   Port: 5432"
    echo "   Database: chatapp_db"
    echo "   Username: chatapp"
    echo "   Password: chatapp_password"
else
    echo "✅ PostgreSQL started successfully!"
fi

echo ""
echo "🔍 Database Connection Details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: chatapp_db"
echo "   Username: chatapp"
echo "   Password: chatapp_password"
echo ""
echo "   Connection URL: postgresql://chatapp:chatapp_password@localhost:5432/chatapp_db"