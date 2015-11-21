#!/bin/bash
set -euo pipefail
VENV=/opt/app/env
if [ ! -d $VENV ] ; then
    virtualenv $VENV
else
    echo "$VENV exists, moving on"
fi

set +o pipefail
secret_key=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 24)
set -o pipefail

cat << EOF > /opt/app/local_settings.py
SQLALCHEMY_DATABASE_URI='postgresql://sandstorm@/pg-discuss'
SECRET_KEY='$secret_key'
# How do we know if we should keep the cookie secure?
SESSION_COOKIE_SECURE = False
ENABLE_EXT_BLESSED_CORS = True
# Can't seem to send custom headers, so CSRF token is disabled.
ENABLE_EXT_BLESSED_CSRF_TOKEN = False
EOF

# Install Python packages
$VENV/bin/pip install -e /opt/app
$VENV/bin/pip install -e /opt/app/blessed_extensions

# Spawn postgresql
sudo su sandstorm -c '/usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c config_file=/etc/postgresql/9.4/main/postgresql.conf' &

POSTGRESQL_SOCKET_FILE=/var/run/postgresql/.s.PGSQL.5432
# Wait for postgresql to bind its socket
while [ ! -e $POSTGRESQL_SOCKET_FILE ] ; do
    echo "waiting for postgresql to be available at $POSTGRESQL_SOCKET_FILE"
    sleep .2
done

sudo su - postgres -c 'createuser -l --no-password -e sandstorm'
sudo su - postgres -c 'createdb -E UTF-8 pg-discuss'

sudo su sandstorm -c '. /opt/app/env/bin/activate \
    && export PG_DISCUSS_SETTINGS_FILE=/opt/app/local_settings.py \
    && pgd-admin db upgrade -d /opt/app/migrations \
    && pgd-admin db upgrade -d /opt/app/ext_migrations'

# Gracefully shutdown postgresql and move the data files
sudo kill `sudo cat /var/lib/postgresql/9.4/main/postmaster.pid` && /bin/true
while [ -e $POSTGRESQL_SOCKET_FILE ] ; do
    echo "waiting for postgresql to shut down"
    sleep .2
done
echo 'moving database files to /opt/app/postgresql'
sudo cp -r /var/lib/postgresql /opt/app/
exit
