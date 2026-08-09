#!/bin/bash

echo "Starting test database..."
sudo docker-compose up -d test-db

echo "Waiting for test database to be ready..."
until sudo docker-compose exec -T test-db pg_isready -U test_user -d test_db | grep -q "accepting connections"; do
  echo "Waiting..."
  sleep 1
done

echo "Database is ready!"

echo "Running tests..."
DATABASE_URL=postgresql://test_user:test_pass@localhost:5433/test_db pytest test_main.py -v

echo "Cleaning up..."
sudo docker-compose stop test-db
sudo docker-compose rm -f test-db
