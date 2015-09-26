import pg_discuss.app


def test_app_factory():
    """Generate a WSGI application object and assert it has expected
    attributes."""
    app = pg_discuss.app.app_factory()
    assert app.config
    assert app.migrate
    assert app.script_manager
    assert app.admin_login_manager
    assert app.ext_mgr_all
    assert app.identity_policy_mgr.identity_policy
    assert app.comment_renderer
    assert app.json_encoder
    assert app.ext_mgr
