from pg_discuss.app import app_factory

app = app_factory()

if __name__ == '__main__':
    app.manager.run()
else:
    # If not running a management command, set log level and log configuration.
    # Set up logging
    app.logger.setLevel(app.config['LOGLEVEL'])

    # Log configuration parameters
    app.logger.info('Configuration parameters:\n{}'.format(
        '\n'.join([k + '=' + str(v) for k, v in
                   sorted(app.config.items())
                   if k not in app.config['DO_NOT_LOG_VARS']])))

    app.logger.info('Found extensions/drivers:\n{}'.format(
        '\n'.join([e.name for e in app.ext_mgr_all.extensions])))

    app.logger.info('Enabled IdentityPolicy driver:\n{}'.format(
        app.identity_policy_loader.extensions[0].name))

    app.logger.info('Enabled CommentRenderer driver:\n{}'.format(
        app.comment_renderer_loader.extensions[0].name))

    app.logger.info('Enabled JSONEncoder driver:\n{}'.format(
        app.json_encoder_loader.extensions[0].name))


    app.logger.info('Enabled extensions:\n{}'.format(
        '\n'.join([e.name for e in app.ext_mgr.extensions])))
    # Make `application` alias for uwsgi/pypy
    # See https://github.com/unbit/uwsgi/issues/900
    application = app
