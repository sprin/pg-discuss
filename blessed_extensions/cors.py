from flask.ext.cors import CORS

from pg_discuss.ext import AppExtBase

class CorsExt(AppExtBase):
    def init_app(self, app):
        CORS(app, supports_credentials=True)
