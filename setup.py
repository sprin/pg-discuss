import sys
import os
from setuptools import setup
from setuptools.command.develop import develop

PYPY = hasattr(sys, 'pypy_version_info')

requires = [
    'SQLAlchemy>=1.0',
    'flask>=0.10, <1.0',
    'alembic>=0.8.0',
    'Flask-SQLAlchemy>=2.0',
    'Flask-Script>=2.0',
    'Flask-Migrate>=1.5.0',
    'Flask-Login>=0.3.0',
    'Flask-WTF>=0.12',
    'voluptuous>=0.8',
    'stevedore>=1.7',
    'flask-cors>=2.1',
    'simplejson>=3.8',
    'misaka>=2.0.0',
]

if PYPY:
    requires += ['psycopg2cffi>=2.7']
else:
    requires += ['psycopg2>=2.6']


def get_data_files_list(paths):
    data_files = []
    for path in paths:
        for root, dirnames, filenames in os.walk(path):
            if not root.endswith('__pycache__'):
                full_filenames = [
                    os.path.join(root, f) for f in filenames
                    if not f.endswith('.pyc')]
                data_files.append([root, full_filenames])
    return data_files


class DevelopDocs(develop):
    """Custom command to require docs dependencies."""

    def __init__(self, *args, **kwargs):
        global requires
        requires += ['sphinx>=1.3.1']
        develop.__init__(self, *args, **kwargs)


class DevelopTests(develop):
    """Custom command to require test dependencies."""

    def __init__(self, *args, **kwargs):
        global requires
        requires += [
            'pytest>=2.8.0',
            'pytest-cov>=2.1.0',
        ]
        develop.__init__(self, *args, **kwargs)

setup(
    name='pg-discuss',
    version='1.0b1',

    description='A comment system backend on top of PostgreSQL',
    license='MIT',

    author='Steffen Prince',
    author_email='steffen@sprin.io',

    url='https://pg-discuss.sprin.io',
    download_url='https://github.com/sprin/pg-discuss',

    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Intended Audience :: Developers',
                 'Environment :: Web Environment',
                 'Framework :: Flask',
                 ],

    platforms=['Any'],

    provides=['pg_discuss'],
    packages=['pg_discuss', 'pg_discuss.drivers'],
    include_package_data=True,
    package_data={'pg_discuss': ['*.html', '*.js', '*.svg']},
    data_files=(
        get_data_files_list(['isso', 'migrations', 'ext_migrations',
                             'blessed_extensions'])
        + [['', ['uwsgi.ini', 'main.py']]]),

    # Entrypoints for drivers included in core. We need to include basic
    # drivers in core so that the app is functional without the
    # `blessed_extensions` package or additional driver packages.
    entry_points={
        'pg_discuss.ext': [
            'core_escaping_renderer = pg_discuss.drivers.escaping_renderer:EscapingRenderer',
            'core_null_identity_policy = pg_discuss.drivers.null_identity_policy:NullIdentityPolicy',
            'core_iso_date_json_encoder = pg_discuss.drivers.iso_date_json_encoder:IsoDateJSONEncoder',
        ],
        'console_scripts': [
            'pgd-admin = pg_discuss.management:execute_from_command_line',
        ],
    },

    zip_safe=False,

    install_requires=requires,

    cmdclass={
        'develop_docs': DevelopDocs,
        'develop_tests': DevelopTests,
    },
)
