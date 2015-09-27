from werkzeug.contrib.profiler import ProfilerMiddleware

from pg_discuss import ext


class ProfilerExt(ext.AppExtBase):
    def init_app(self, app):
        app.config.setdefault('PROFILER_RESTRICTIONS', [20])
        app.config['PROFILE'] = True
        restrictions = app.config['PROFILER_RESTRICTIONS']
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                          restrictions=restrictions)
