#!/bin/bash
# Wait for the database to be ready
while ! pg_isready -h db -p 5432 > /dev/null 2> /dev/null; do
    echo "Waiting for database to be ready..."
    sleep 2
done

# Run the database migrations and data initialization
echo "Initializing database..."
python -c "
from database import Base, engine;
Base.metadata.create_all(bind=engine)
"
python db_manager.py  # This script loads questions into the database

# Start the web server
exec "$@"
