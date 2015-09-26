#!/bin/sh
set -x
sphinx-apidoc -o docs/source/api -e pg_discuss \
    && sphinx-apidoc -o docs/source/api -e blessed_extensions \
    && cd docs \
    && make html
