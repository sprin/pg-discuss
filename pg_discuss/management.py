from pg_discuss.app import app_factory

app = app_factory()


def execute_from_command_line():
    app.script_manager.run()
