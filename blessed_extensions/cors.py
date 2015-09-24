import flask_cors

from pg_discuss import ext

class CorsExt(ext.AppExtBase):
    def init_app(self, app):
        flask_cors.CORS(app, supports_credentials=True)
