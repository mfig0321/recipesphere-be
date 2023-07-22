#!/bin/sh

# wait for postgres container to start
echo "waiting for database to start"
sleep 30
echo "--------------------------------"

# install dependencies
cd /code
pipenv install --dev

# change to application root
cd /code/application


# run migrations
pipenv run python manage.py migrate

# pipenv run python manage.py loaddata fixtures/*.json

# # coverage implementation
# pipenv run coverage run -m pytest
# pipenv run coverage html

# start dev server
pipenv run python manage.py runserver 0.0.0.0:8000

