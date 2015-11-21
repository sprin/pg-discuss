#!/bin/bash
set -euo pipefail

# Wipe /var/run, since pidfiles and socket files from previous launches should go away
# TODO someday: I'd prefer a tmpfs for these.
rm -rf /var/run
mkdir -p /var/run

mkdir /var/lib
mkdir -p /var/log

cp -r /opt/app/postgresql /var/lib/
chmod 0700 /var/lib/postgresql/9.4/main
mkdir -p /var/log/postgresql
mkdir -p /var/run/postgresql

mkdir -p /var/lib/nginx
mkdir -p /var/log/nginx

UWSGI_SOCKET_FILE=/var/run/uwsgi.sock

# Spawn postgresql
echo 'starting postgresql'
/usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c config_file=/etc/postgresql/9.4/main/postgresql.conf &

POSTGRESQL_SOCKET_FILE=/var/run/postgresql/.s.PGSQL.5432
# Wait for postgresql to bind its socket
while [ ! -e $POSTGRESQL_SOCKET_FILE ] ; do
    echo "waiting for postgresql to be available at $POSTGRESQL_SOCKET_FILE"
    sleep .2
done

# Spawn uwsgi
HOME=/var PG_DISCUSS_SETTINGS_FILE=/opt/app/local_settings.py \
        uwsgi \
        --socket $UWSGI_SOCKET_FILE \
        --plugin python \
        --venv /opt/app/env \
        --ini /opt/app/.sandstorm/uwsgi.ini &

# Wait for uwsgi to bind its socket
while [ ! -e $UWSGI_SOCKET_FILE ] ; do
    echo "waiting for uwsgi to be available at $UWSGI_SOCKET_FILE"
    sleep .2
done

# Start nginx.
/usr/sbin/nginx -g "daemon off;"

