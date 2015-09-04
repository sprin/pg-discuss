from flask.ext.cors import CORS

from pg_discuss import ext

class CorsExt(ext.AppExtBase):
    def init_app(self, app):
        CORS(app, supports_credentials=True)
