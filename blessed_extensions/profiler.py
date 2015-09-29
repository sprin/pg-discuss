from werkzeug.contrib.profiler import ProfilerMiddleware

from pg_discuss import ext


class ProfilerExt(ext.AppExtBase):
    def init_app(self, app):
        app.config.setdefault('PROFILER_RESTRICTIONS', [20])
        app.config.setdefault('PROFILER_DIR', None)
        app.config['PROFILE'] = True
        restrictions = app.config['PROFILER_RESTRICTIONS']
        profile_dir = app.config['PROFILER_DIR']
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            restrictions=restrictions,
            profile_dir=profile_dir)
