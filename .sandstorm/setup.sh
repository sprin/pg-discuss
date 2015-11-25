#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx uwsgi uwsgi-plugin-python build-essential python-dev python-virtualenv gcc postgresql libpq-dev libffi-dev
# Set up nginx conf
unlink /etc/nginx/sites-enabled/default
cat > /etc/nginx/sites-available/sandstorm-python <<EOF
server {
    listen 8000 default_server;
    listen [::]:8000 default_server ipv6only=on;

    # Allow arbitrarily large bodies - Sandstorm can handle them, and requests
    # are authenticated already, so there's no reason for apps to add additional
    # limits by default.
    client_max_body_size 0;

    server_name localhost;
    root /opt/app;
    location /static/embed.min.js {
        alias /opt/app/isso/js/embed.min.js;
    }
    location /static/ {
        alias /opt/app/pg_discuss/static/;
    }
    location / {
        uwsgi_pass unix:///var/run/uwsgi.sock;
        include uwsgi_params;
    }
}
EOF
ln -s /etc/nginx/sites-available/sandstorm-python /etc/nginx/sites-enabled/sandstorm-python
# patch nginx conf to not bother trying to setuid, since we're not root
# also patch errors to go to stderr, and logs nowhere.
sed --in-place='' \
        --expression 's/^user www-data/#user www-data/' \
        --expression 's#^pid /run/nginx.pid#pid /var/run/nginx.pid#' \
        --expression 's/^\s*error_log.*/error_log stderr;/' \
        --expression 's/^\s*access_log.*/access_log off;/' \
        /etc/nginx/nginx.conf

# patch postgresql.conf to not listen to localhost, and not use shmem
sed --in-place='' \
        --expression 's/^#listen_addresses.*/listen_addresses = '\'\''/' \
        --expression 's/dynamic_shared_memory_type.*/dynamic_shared_memory_type = none/' \
        --expression 's/ssl =*/ssl = false/' \
        /etc/postgresql/9.4/main/postgresql.conf

# patch pg_hba.conf to trust all local connections
sed --in-place='' \
        --expression 's/^local.*/local all all trust/' \
        /etc/postgresql/9.4/main/pg_hba.conf

service nginx stop
service postgresql@9.4-main stop
systemctl disable nginx
systemctl disable postgresql@9.4-main

chown -R sandstorm:sandstorm /var/lib/postgresql
chown -R sandstorm:sandstorm /var/run/postgresql
chown -R sandstorm:sandstorm /etc/postgresql
