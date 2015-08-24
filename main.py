from pg_discuss.app import app_factory

app = app_factory()

if __name__ == '__main__':
    app.manager.run()
