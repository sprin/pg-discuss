import sys
from setuptools import setup, find_packages

PYPY = hasattr(sys, 'pypy_version_info')

requires = [
    'SQLAlchemy>=1.0',
    'flask>=0.10',
    'alembic>=0.8.0',
    'Flask-SQLAlchemy>=2.0',
    'Flask-Script>=2.0',
    'Flask-Migrate>=1.5.0',
    'voluptuous>=0.8',
    'stevedore>=1.7',
    'flask-cors>=2.1',
    'simplejson>=3.8',
    'misaka==2.0.0b1.post2',
]

if PYPY:
    requires += ['psycopg2cffi>=2.7']
else:
    requires += ['psycopg2>=2.6']

setup(
    name='pg-discuss',
    version='1.0',

    description='A comment system backend on top of PostgreSQL',
    license='MIT',

    author='Steffen Prince',
    author_email='steffen@sprin.io',

    url='https://sprin.io',
    download_url='https://github.com/sprin/pg-discuss',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Intended Audience :: Developers',
                 'Environment :: Web Environment',
                 'Framework :: Flask',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=['pg_discuss',
              ],
    packages=find_packages(),

    zip_safe=False,

    install_requires=requires,
)

