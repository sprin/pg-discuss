from werkzeug.contrib.profiler import ProfilerMiddleware

from pg_discuss import ext

#: Profile report restrictions.
#: See: https://docs.python.org/2/library/profile.html#pstats.Stats.print_stats
PROFILER_RESTRICTIONS = [20]
#: Directory to save profiler results. Results can be interpreted by a
#: graphical program such as SnakeViz (highly recommended):
#: https://jiffyclub.github.io/snakeviz/
PROFILER_DIR = None


class ProfilerExt(ext.AppExtBase):
    def init_app(self, app):
        app.config.setdefault('PROFILER_RESTRICTIONS', PROFILER_RESTRICTIONS)
        app.config.setdefault('PROFILER_DIR', PROFILER_DIR)
        app.config['PROFILE'] = True
        restrictions = app.config['PROFILER_RESTRICTIONS']
        profile_dir = app.config['PROFILER_DIR']
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            restrictions=restrictions,
            profile_dir=profile_dir)
