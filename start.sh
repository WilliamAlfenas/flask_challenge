#!/usr/bin/env bash

#sudo apt-get install libpq-dev
#pip3 install -r requirements.txt

# PGUSER="postgres"
# PGPASSWORD="postgres"
# PGDATABASE="vessels_db"
# PGDATABASETEST="vessels_db_test"
# PGPORT="5432"
# PGHOST="localhost"

# while ! pg_isready -q -h $PGHOST -p $PGPORT -U $PGUSER
# do
#   echo "$(date) - waiting for database to start"
#   sleep 2
# done

# Create database if it doesn't exist.
# if [[ -z `psql -Atqc "\\list $PGDATABASE"` ]]; then
#   echo "Database $PGDATABASE does not exist. Creating..."
#   createdb -U $PGUSER -W -E UTF8 $PGDATABASE -l en_US.UTF-8 -T template0 
#   echo "Database $PGDATABASE created."
# fi

# Create database if it doesn't exist.
# if [[ -z `psql -Atqc "\\list $PGDATABASETEST"` ]]; then
#   echo "Database $PGDATABASETEST does not exist. Creating..."
#   createdb -O $PGUSER -E UTF8 $PGDATABASETEST -l en_US.UTF-8 -T template0 
#   echo "Database $PGDATABASETEST created."
# fi

export FLASK_APP="manage.py"
export FLASK_DEBUG=1


# flask db init
# flask db migrate
# flask db upgrade

rm -rf migrations
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade

# pytest -v --disable-pytest-warnings

flask run -h 0.0.0.0 -p 5000
