FROM centos:7.1.1503
MAINTAINER Steffen Prince <steffen@sprin.io>

EXPOSE 8080


# Disable fastermirror plugin - not using it is actually faster.
RUN sed -ri 's/^enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf

# Set LANG and LC_ALL
ENV LANG='en_US.UTF-8' LC_ALL='en_US.UTF-8' PYTHONIOENCODING='UTF-8'

# Create a healthcheck.html for haproxy/external uptime monitoring checks
RUN /bin/echo OK > /opt/healthcheck.html

# Install EPEL, gcc, tar, mailcap (mime.types), ffi (for misaka), pcre (uwsgi)
RUN yum install -y \
    epel-release \
    gcc \
    tar \
    mailcap \
    libffi-devel \
    pcre-devel \
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

# Install Python 3
RUN yum install -y \
    python34 \
    python34-devel \
    && yum clean all

RUN curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3.4 get-pip.py \
    && rm get-pip.py

# Add and install Python modules for docs
WORKDIR /src
ADD setup.py /src/setup.py
RUN python3.4 setup.py test
ADD blessed_extensions/setup.py /src/blessed_extensions/setup.py
RUN python3.4 blessed_extensions/setup.py develop

COPY . /src

# Build the docs

CMD ["python3.4", "-m", "nose", "--with-coverage", "--cover-package=pg_discuss"]
