============
Installation
============

pg-discuss is a Python `WSGI application`_ that runs in a
`WSGI server`_. It depends on a connection to `PostgreSQL`_ database, which
may be installed on the same host or a different one.

.. _`WSGI application`: https://www.python.org/dev/peps/pep-3333/#the-application-framework-side
.. _`WSGI server`: https://www.python.org/dev/peps/pep-3333/#the-server-gateway-side
.. _`PostgreSQL`: http://www.postgresql.org/

The `Container Installation`_ guide covers building from the included
Dockerfile and running it. This is the quickest way to get up and running on a
system with a container runtime such as `Docker`_ or `rkt`_.

.. _`Docker`: https://github.com/docker/docker#docker-the-container-engine-
.. _`rkt`: https://github.com/coreos/rkt#rkt---app-container-runtime

The `Traditional Installation`_ guide covers preparing the Python environment,
installing pg-discuss and it's extensions, installing/configuring the `uWSGI`_
WSGI server, and setting up the PostgreSQL database.

.. _`uWSGI`: https://uwsgi-docs.readthedocs.org/en/latest/WSGIquickstart.html

Container Installation
======================

This installation creates and runs a container image, inside of which is a
`uwsgi` binary running the pg-discuss app.

First, jump to `Set up PostgreSQL`_ to create the database for the container to
connect to. For evaluation purposes, you may instead pair this with a
`PostgreSQL container image`_ if you would do not want to install PostgreSQL on
your system, but this is not recommended for production.

.. _`PostgreSQL container image`: https://github.com/docker-library/postgres/tree/master/9.5

Grab a `release tarball` to get the Python source
and Dockerfile needed to build the image.

.. _`release tarball`: https://github.com/mitsuhiko/flask/releases

After extracting the release tarball, enter the directory. Create a
`localsettings.py` file in the root for your custom configuration: see
:ref:`Configuration` for details. If you don't have any custom configuration,
just create an empty file.

Build the image:

.. code-block:: console

   docker build -t pg-discuss .

Run the image. In this example, we give the container a name of "pg-discuss"
and populate it's environment from the file `env`. The `env` file contains our
connection parameters and secrets, so that we are not required to bake them in
to the image. We also expose publish the container's port  8080, which uwsgi is
bound to, to the host's port 8080.

.. code-block:: console

   docker run -d --name pg-discuss --env-file env -p 8080:8080 pg-discuss

.. warning::

   While running pg-discuss in a container in production is one of the
   recommended deployments, you must ensure that you have a means for keeping
   your containers up-to-date. Since containers can't be updated in place, you
   must have a strategy for rebuilding images when updates are required. The
   provided Dockerfile is only a starting point: you must take care to ensure
   that the Dockerfile you use will build an up-to-date image.

Traditional Installation
========================

Prepare the Python Environment
------------------------------

pg-discuss will run with either Python 2.7, or 3.4+. Older versions may work,
but are not supported. Python 3 is preferred since it is the Python developers'
focus for security and performance enhancements.  These examples will assume a
3.4+ installation with a binary named `python3`, which includes the `pip`_
package installation tool. If `pip` is not included in your Python
installation, follow these instructions to `install pip`_.

.. _`pip`: https://pip.pypa.io/en/latest/installing/#pip-included-with-python
.. _`install pip`: https://pip.pypa.io/en/latest/installing/#install-pip

You have two choices for preparing the Python package environment:

 - Create a `virtualenv`_ for pg-discuss. This is appropriate for servers
   hosting multiple applications, not using virtualization.
 - Install pg-discuss using the system Python packages. This is usually only
   appropriate if you are using a dedicated VM or creating a container image.

.. _`virtualenv`: https://virtualenv.pypa.io/en/latest/userguide.html

virtualenv
..........

Install virtualenv from your package manager. You will probably have the choice
of `python-virtualenv` and `python3-virtualenv`.

If `virtualenv` is not available from your system's package manager, you may
install via `pip`:

.. code-block:: console

   sudo python3 -m pip install virtualenv

As the user you wish to run WSGI server as (eg, the `uwsgi` user), create the
virtualenv in a directory the user can read:

.. code-block:: console

    python3 -m virtualenv /opt/pg-discuss

Install pg-discuss
------------------

pg-discuss is available via pip from `PyPI`. This will install PyPI and it's
dependencies:

.. code-block:: console

   python3 -m pip install pg-discuss

.. _`PyPI`:https://pypi.python.org/pypi

pg-discuss depends on extensions for most of it's useful functionality. A set
of "blessed extensions" - blessed by the maintainers - are included. To install
these:

.. code-block:: console

   PG_DISCUSS_PATH=/opt/pg-discuss/lib/python3.4/site-packages/pg_discuss/
   python3 $PG_DISCUSS_PATH/blessed_extensions/setup.py install

Install and Configure uwsgi
---------------------------

Install the `uwsgi` package through your package manager.

If `uwsgi` is not available from your system's package manager, you may
install via `pip`:

.. code-block:: console

   sudo python3 -m pip install uwsgi

`uwsgi` has a great many `configuration options`_, but the provided uwsgi.ini
is a good starting point. Place this at `/opt/pg-discuss/uwsgi.ini`.

.. todo::

   Link to uwsgi.ini

.. todo::

   Change uwsgi.ini and Dockerfiles to use /opt.

.. _`configuration options`: https://uwsgi-docs.readthedocs.org/en/latest/Options.html

To run `uwsgi` and load the app:

.. code-block:: console

   uwsgi --ini /opt/pg-discuss/uwsgi.ini

Running as a systemd service
----------------------------

When running in production, you will want to set up `uwsgi` to run as a system
service, so that it starts on boot and we can use the service manager to
control it. `systemd`_ is the service manager now used in most Linux
distributions.

.. _`systemd`: https://wiki.freedesktop.org/www/Software/systemd/

We can create this unit file at /etc/systemd/system/pg-discuss.service:

.. code-block:: ini

   [Unit]
   Description=pg-discuss comment server

   [Service]
   ExecStart=uwsgi --ini /opt/pg-discuss/uwsgi.ini

   [Install]
   WantedBy=multi-user.target

Now we can enable and start it:


.. code-block:: console

   systemctl enable pg-discuss
   systemctl start pg-discuss

Now pg-discuss is running, but we have no database to connect to yet!

Set up PostgreSQL
-----------------

The "pg" in pg-discuss stands for PostgreSQL. The minimum required version is
9.4, however 9.5+ is strongly recommended. Several useful extensions leverage
the `powerful JSON manipulation`_ functions in PostgreSQL 9.5, although slower
fallbacks are provided for 9.4.

.. _`powerful JSON manipulation`: http://www.postgresql.org/docs/9.5/static/functions-json.html#FUNCTIONS-JSON-PROCESSING-TABLE

.. todo::

   Provide slower fallbacks for 9.4 as promised.

Check to see if your distribution carries 9.5 (or 9.4, if you don't mind using
slower fallbacks):

 - For rpm-based distros (Fedora/CentOS/RHEL): `yum info postgresql`
 - For apt-based distros (Debian/Ubuntu): `apt-cache policy postgresql`

If your distro does not carry the version you want, you can install 9.5 via the
official PGDG repositories:

 - For rpm-based distros (Fedora/CentOS/RHEL): http://yum.postgresql.org/
 - For apt-based distros (Debian/Ubuntu): http://apt.postgresql.org/

Example installation via PGDG on CentOS 7:

.. code-block:: console

  sudo yum install -y http://yum.postgresql.org/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-1.noarch.rpm
  sudo yum install -y postgresql95-server

.. note::

   From this point, you should check the documentation for the
   distro/package you have installed. Different distros/packages have very
   different preferences for creating the cluster and setting up a systemd
   service.

With PostgreSQL installed, you will now need to prepare the database storage
area, called a `creating a cluster`. The `initdb` utility does this.

.. _`creating a cluster`: http://www.postgresql.org/docs/9.5/static/creating-cluster.html

First, we need to create the `postgres` user if there is not one already
created by the install process:

.. code-block:: console

   sudo useradd postgres

We may need to create the parent directory as root, then run `initdb` as the
`postgres` user. Assuming `initdb` was installed to /usr/pgsql-9.5/bin/initdb,
and the unit file expects the cluster directory to be in `/var/lib/pgsql/9.5`:

.. code-block:: console

   $ sudo mkdir /var/lib/pgsql
   $ sudo chown postgres /var/lib/pgsql
   $ sudo su postgres
   $ sudo /usr/pgsql-9.5/bin/postgresql95-setup initdb

Enable and start the service. Assuming your package installed a unit file
called `postgresql95`:

.. code-block:: console

   systemctl enable postgresql95
   systemctl start postgresql95

Create a user for pg-discuss:

.. code-block:: console

   createuser -P -l -e pg-discuss
   sudo su - postgres -c 'createdb -E UTF-8 pg-discuss'

Congrats!
=========

With uwsgi, pg-discuss, PostgreSQL installed, we just need to configure
pg-discuss before we are fully up and running. Head on over to the
]:ref:`Configuration` section.
