FROM centos:7.1.1503
MAINTAINER Steffen Prince <steffen@sprin.io>

EXPOSE 8080

CMD ["/usr/bin/uwsgi", "--ini", "uwsgi.ini"]

# Disable fastermirror plugin - not using it is actually faster.
RUN sed -ri 's/^enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf

# Set LANG and LC_ALL
ENV LANG='en_US.UTF-8' LC_ALL='en_US.UTF-8' PYTHONIOENCODING='UTF-8'

# Create a healthcheck.html for haproxy/external uptime monitoring checks
RUN /bin/echo OK > /opt/healthcheck.html

# Install EPEL, gcc, tar, mailcap (mime.types), ffi (for misaka), pcre (uwsgi),
# and pypy dependencies, as well as a packaged pypy.
RUN yum install -y \
    epel-release \
    gcc \
    tar \
    mailcap \
    libffi-devel \
    pcre-devel \
    bzip2 \
    && yum clean all

# Install Postgres client tools and headers for Postgres
RUN yum install -y \
    http://yum.postgresql.org/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-1.noarch.rpm; \
    yum install -y \
    postgresql95 \
    postgresql95-devel \
    && yum clean all

# Add Postgres bin dir to path
ENV PATH /usr/pgsql-9.5/bin:$PATH

# Download pre-built pypy binary and library
RUN curl -OL https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-2.6.1-linux_x86_64-portable.tar.bz2 -P /tmp/ \
    && tar -xjf pypy-2.6.1-linux_x86_64-portable.tar.bz2 -C /opt \
    && ln -s /opt/pypy-2.6.1-linux_x86_64-portable/bin/libpypy-c.so /usr/lib/ \
    && ldconfig \
    && ln -s /opt/pypy-2.6.1-linux_x86_64-portable/bin/* /usr/bin/ \
    && rm pypy-2.6.1-linux_x86_64-portable.tar.bz2

RUN curl -O https://bootstrap.pypa.io/get-pip.py \
    && pypy get-pip.py \
    && rm get-pip.py

# Install uwsgi
RUN pypy -m pip --disable-pip-version-check install uwsgi \
    && ln -s /opt/pypy-2.6.1-linux_x86_64-portable/bin/uwsgi /usr/bin/

# Add and install Python modules
WORKDIR /src
ADD setup.py /src/setup.py
RUN pypy setup.py develop
ADD blessed_extensions/setup.py /src/blessed_extensions/setup.py
RUN pypy blessed_extensions/setup.py develop

# Add uwsgi.ini
ADD uwsgi.ini /src/uwsgi.ini
