from __future__ import with_statement

import re
import unittest
from flask import Flask
from pg_discuss.csrf import CsrfProtect
from pg_discuss.csrf import validate_csrf, generate_csrf
from pg_discuss._compat import to_unicode

csrf_token_input = re.compile(
    r'([0-9a-z#A-Z-\.]*)'
)

def get_csrf_token(data):
    match = csrf_token_input.search(to_unicode(data))
    assert match
    return match.groups()[0]

class TestCSRF(unittest.TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.secret_key = "secret"

        @app.route('/csrftoken', methods=['GET'])
        def csrftoken():
            return generate_csrf()

        return app

    def setUp(self):
        app = self.create_app()
        app.config['SECRET_KEY'] = "a poorly kept secret."
        csrf = CsrfProtect(app)
        self.csrf = csrf

        @app.route('/', methods=['GET', 'POST'])
        def csrf_protected():
            return 'protected'

        @csrf.exempt
        @app.route('/csrf-exempt', methods=['GET', 'POST'])
        def csrf_exempt():
            return 'exempt'

        @csrf.exempt
        @app.route('/csrf-protect-method', methods=['GET', 'POST'])
        def csrf_protect_method():
            csrf.protect()
            return 'protected'

        self.app = app
        self.client = self.app.test_client()

    def test_missing_secret_key(self):
        self.app.config['SECRET_KEY'] = None
        with self.app.test_request_context():
            with self.assertRaises(ValueError):
                generate_csrf()

    def test_csrf_check_default_false(self):
        app = self.create_app()
        app.config['CSRF_CHECK_DEFAULT'] = False

        csrf = CsrfProtect(app)
        self.csrf = csrf

        @app.route('/', methods=['GET', 'POST'])
        def csrf_protected():
            return 'protected'

        self.app = app
        self.client = self.app.test_client()

        response = self.client.post("/", data={"name": "danny"})
        print response.data
        assert response.status_code == 200

    def test_invalid_csrf(self):
        response = self.client.post("/", data={"name": "danny"})
        assert response.status_code == 403
        assert b'token missing' in response.data

    def test_invalid_csrf2(self):
        # tests with bad token
        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={'X-CSRF-Token': "9999999999999##test"
            # will work only if greater than time.time()
        })
        assert response.status_code == 403

    def test_invalid_csrf3(self):
        # tests with bad token
        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={'X-CSRF-Token': "foo"
        })
        assert response.status_code == 403

    def test_invalid_secure_csrf3(self):
        # test with multiple separators
        response = self.client.post(
            "/",
            data={"name": "danny"},
            # will work only if greater than time.time()
            base_url='https://localhost/',
        )
        assert response.status_code == 403

    def test_valid_csrf(self):
        response = self.client.get("/csrftoken")
        csrf_token = get_csrf_token(response.data)

        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={'X-CSRF-Token': csrf_token},
            base_url='https://localhost/',
            environ_base={
                'HTTP_REFERER': 'https://localhost/',
            },
        )
        assert b'protected' in response.data

    def test_invalid_secure_csrf(self):
        response = self.client.get("/csrftoken", base_url='https://localhost/')
        csrf_token = get_csrf_token(response.data)

        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={'X-CSRF-Token': csrf_token},
            base_url='https://localhost/',
        )
        assert response.status_code == 403
        assert b'failed' in response.data

        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://example.com/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 403
        assert b'not match' in response.data

        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'http://localhost/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 403
        assert b'not match' in response.data

        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://localhost:3000/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 403
        assert b'not match' in response.data

    def test_valid_secure_csrf(self):
        response = self.client.get("/csrftoken", base_url='https://localhost/')
        csrf_token = get_csrf_token(response.data)
        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://localhost/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 200

    def test_valid_csrf_method(self):
        response = self.client.get("/csrftoken")
        csrf_token = get_csrf_token(response.data)

        response = self.client.post(
            "/csrf-protect-method",
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://localhost/',
            },
        )
        assert response.status_code == 200

    def test_invalid_csrf_method(self):
        response = self.client.post("/csrf-protect-method", data={"name": "danny"})
        assert response.status_code == 403

        response = self.client.post("/", data={"name": "danny"})
        assert response.status_code == 403
        assert b'token missing' in response.data

    def test_empty_csrf_headers(self):
        response = self.client.get("/csrftoken", base_url='https://localhost/')
        csrf_token = get_csrf_token(response.data)
        self.app.config['CSRF_HEADERS'] = list()
        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://localhost/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 403

    def test_custom_csrf_headers(self):
        response = self.client.get("/csrftoken", base_url='https://localhost/')
        csrf_token = get_csrf_token(response.data)
        self.app.config['CSRF_HEADERS'] = ['X-XSRF-TOKEN']
        response = self.client.post(
            "/",
            data={"name": "danny"},
            headers={
                'X-XSRF-TOKEN': csrf_token,
            },
            environ_base={
                'HTTP_REFERER': 'https://localhost/',
            },
            base_url='https://localhost/',
        )
        assert response.status_code == 200

    def test_not_endpoint(self):
        response = self.client.post('/not-endpoint')
        assert response.status_code == 404

    def test_testing(self):
        self.app.testing = True
        self.client.post("/", data={"name": "danny"})

    def test_csrf_exempt(self):
        response = self.client.get("/csrftoken")
        csrf_token = get_csrf_token(response.data)

        response = self.client.post(
            "/csrf-exempt",
            data={"name": "danny"},
            headers={
                'X-CSRF-Token': csrf_token,
            },
        )
        assert b'exempt' in response.data

    def test_validate_csrf(self):
        with self.app.test_request_context():
            assert not validate_csrf('ff##dd')
            csrf_token = generate_csrf()
            assert validate_csrf(csrf_token)

    def test_validate_not_expiring_csrf(self):
        with self.app.test_request_context():
            csrf_token = generate_csrf(time_limit=False)
            assert validate_csrf(csrf_token, time_limit=False)
