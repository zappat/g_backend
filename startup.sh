#!/bin/bash

# Wait for database to be ready
python manage.py wait_for_db

# Run migrations
python manage.py migrate

# Seed categories
python manage.py seed_categories

# Start Daphne ASGI server
exec daphne -b 0.0.0.0 -p 8000 app.asgi:application 