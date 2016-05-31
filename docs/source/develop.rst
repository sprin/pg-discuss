===============
Developer Setup
===============

Prerequisites
=============

Dependencies:

 - Python (3.4 or greater recommended for development)
 - Python development headers
 - Python virtualenv
 - PostgreSQL 9.5 server or greater
 - PostgreSQL develpment headers
 - "C Development Tools and Libraries" (gcc, make, glibc headers)
 - libffi headers

You do not need to install `uwsgi` systemwide; you should install `uwsgi` via
`pip` in the virtualenv (see below).

Ensure PostgreSQL is running and a cluster is initialized. Create a user in
PostgreSQL that matches the user you will run the app under.  Create the
database `pg-discuss` and make sure your user can connect to it via the Unix
domain socket.

Installing and Configuring in a Virtualenv
==========================================

Create a new virtual environment:

.. code-block:: console

   mkdir venv
   python3 -m virtualenv venv/pg-discuss
   source venv/pg-discuss/bin/activate

Clone the repo:

.. code-block:: console

   git clone git@github.com:sprin/pg-discuss.git

Install dependencies. Assuming your pg_config executable is in
/usr/pgsql-9.5/bin:

.. code-block:: console

   cd pg-discuss
   PATH=$PATH:/usr/pgsql-9.5/bin python -m pip install .
   python -m pip install -e blessed_extensions
   python -m pip install uwsgi

Run the initial schema migrations using the configuration files found in the
`dev` directory:

.. code-block:: console

   cd dev
   pgd-admin db upgrade
   pgd-admin db upgrade --directory ext_migrations/

Finally, from the `dev` directory, run `uwsgi`. The app will show a landing
page that is useful for development purposes on `http://localhost:8080`.

.. code-block:: console

   env $(cat env) uwsgi --ini uwsgi.ini
