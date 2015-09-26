import unittest

import pg_discuss.app


class TestAppFactory(unittest.TestCase):

    def test_app_factory(self):
        """Generate a WSGI application object and assert it has expected
        attributes."""
        app = pg_discuss.app.app_factory()
        self.assertTrue(app.config)
        self.assertTrue(app.migrate)
        self.assertTrue(app.script_manager)
        self.assertTrue(app.admin_login_manager)
        self.assertTrue(app.ext_mgr_all)
        self.assertTrue(app.identity_policy_mgr.identity_policy)
        self.assertTrue(app.comment_renderer)
        self.assertTrue(app.json_encoder)
        self.assertTrue(app.ext_mgr)
