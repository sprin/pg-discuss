import sys

import flask_sqlalchemy

class PgAlchemy(flask_sqlalchemy.SQLAlchemy):
    """Custom subclass of the SQLAlchemy extension that sets the
    connection timezone to UTC. The backend should handle timestamps entirely
    in UTC, with timezone adjustment performed on the client side.
    """
    def apply_driver_hacks(self, app, info, options):
        options['connect_args'] = {"options": "-c timezone=utc"}
        options['isolation_level'] = 'AUTOCOMMIT'

db = PgAlchemy()
# Allow db instance to masquerade as module.
sys.modules[__name__] = db
