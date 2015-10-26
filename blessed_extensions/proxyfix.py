from werkzeug.contrib.fixers import ProxyFix

from pg_discuss import ext

#: Number of HTTP proxies the server is running behind.
NUM_PROXIES = 1


class ProxyFixExt(ext.AppExtBase):
    """Enable the ProxyFix WSGI middleware.

    See:
    http://flask.pocoo.org/docs/0.10/deploying/wsgi-standalone/#proxy-setups

    Do not enable this middleware if the application is not running behind
    a proxy - this will render the app vulnerable to IP spoofing.
    """
    def __init__(self, app):
        self.app = app
        app.config.setdefault('NUM_PROXIES', NUM_PROXIES)

    def init_app(self, app):
        app.wsgi_app = ProxyFix(app.wsgi_app,
                                num_proxies=self.app.config['NUM_PROXIES'])
