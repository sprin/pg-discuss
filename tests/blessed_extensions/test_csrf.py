from __future__ import with_statement

import re
import pytest
from flask import Flask
from blessed_extensions import csrf_token
from pg_discuss._compat import to_unicode

csrf_token_input = re.compile(
    r'([0-9a-z#A-Z-\.]*)'
)


def get_csrf_token(data):
    match = csrf_token_input.search(to_unicode(data))
    assert match
    return match.groups()[0]


def create_app():
    app = Flask(__name__)
    app.secret_key = "secret"

    @app.route('/csrftoken', methods=['GET'])
    def csrftoken():
        return csrf_token.generate_csrf()

    return app


@pytest.fixture
def app():
    """Fixture to create an app with CsrfTokenExt initialized.

    Creates several views for testing.
    """
    app = create_app()
    app.config['SECRET_KEY'] = "a poorly kept secret."
    csrf = csrf_token.CsrfTokenExt(app)
    csrf.init_app(app)
    app.client = app.test_client()

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

    return app


def test_missing_secret_key(app):
    app.config['SECRET_KEY'] = None
    with app.test_request_context():
        with pytest.raises(ValueError):
            csrf_token.generate_csrf()


def test_invalid_csrf(app):
    response = app.client.post("/", data={"name": "danny"})
    assert response.status_code == 403
    assert b'token missing' in response.data


def test_invalid_csrf2(app):
    # tests with bad token
    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={'X-CSRF-Token': "9999999999999##test"}
    )
    assert response.status_code == 403


def test_invalid_csrf3(app):
    # tests with bad token
    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={'X-CSRF-Token': "foo"}
    )
    assert response.status_code == 403


def test_invalid_secure_csrf3(app):
    # test with multiple separators
    response = app.client.post(
        "/",
        data={"name": "danny"},
        # will work only if greater than time.time()
        base_url='https://localhost/',
    )
    assert response.status_code == 403


def test_valid_csrf(app):
    response = app.client.get("/csrftoken")
    token = get_csrf_token(response.data)

    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={'X-CSRF-Token': token},
        base_url='https://localhost/',
        environ_base={
            'HTTP_REFERER': 'https://localhost/',
        },
    )
    assert b'protected' in response.data


def test_invalid_secure_csrf(app):
    response = app.client.get("/csrftoken", base_url='https://localhost/')
    token = get_csrf_token(response.data)

    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={'X-CSRF-Token': token},
        base_url='https://localhost/',
    )
    assert response.status_code == 403
    assert b'failed' in response.data

    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://example.com/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 403
    assert b'not match' in response.data

    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'http://localhost/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 403
    assert b'not match' in response.data

    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://localhost:3000/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 403
    assert b'not match' in response.data


def test_valid_secure_csrf(app):
    response = app.client.get("/csrftoken", base_url='https://localhost/')
    token = get_csrf_token(response.data)
    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://localhost/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 200


def test_valid_csrf_method(app):
    response = app.client.get("/csrftoken")
    token = get_csrf_token(response.data)

    response = app.client.post(
        "/csrf-protect-method",
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://localhost/',
        },
    )
    assert response.status_code == 200


def test_invalid_csrf_method(app):
    response = app.client.post("/csrf-protect-method", data={"name": "danny"})
    assert response.status_code == 403

    response = app.client.post("/", data={"name": "danny"})
    assert response.status_code == 403
    assert b'token missing' in response.data


def test_empty_csrf_headers(app):
    response = app.client.get("/csrftoken", base_url='https://localhost/')
    token = get_csrf_token(response.data)
    app.config['CSRF_TOKEN_HEADERS'] = list()
    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://localhost/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 403


def test_custom_csrf_headers(app):
    response = app.client.get("/csrftoken", base_url='https://localhost/')
    token = get_csrf_token(response.data)
    app.config['CSRF_TOKEN_HEADERS'] = ['X-XSRF-TOKEN']
    response = app.client.post(
        "/",
        data={"name": "danny"},
        headers={
            'X-XSRF-TOKEN': token,
        },
        environ_base={
            'HTTP_REFERER': 'https://localhost/',
        },
        base_url='https://localhost/',
    )
    assert response.status_code == 200


def test_not_endpoint(app):
    response = app.client.post('/not-endpoint')
    assert response.status_code == 404


def test_testing(app):
    app.testing = True
    app.client.post("/", data={"name": "danny"})


def test_csrf_exempt(app):
    response = app.client.get("/csrftoken")
    token = get_csrf_token(response.data)

    response = app.client.post(
        "/csrf-exempt",
        data={"name": "danny"},
        headers={
            'X-CSRF-Token': token,
        },
    )
    assert b'exempt' in response.data


def test_validate_csrf(app):
    with app.test_request_context():
        assert not csrf_token.validate_csrf('ff##dd')
        token = csrf_token.generate_csrf()
        assert csrf_token.validate_csrf(token)


def test_validate_not_expiring_csrf(app):
    with app.test_request_context():
        token = csrf_token.generate_csrf(time_limit=False)
        assert csrf_token.validate_csrf(token, time_limit=False)


def test_csrf_check_default_false():
    """This test does not use the app fixture, since we need to change
    a setting that is used in initialization of the extension.
    """
    app = create_app()
    app.config['CSRF_TOKEN_CHECK_DEFAULT'] = False
    app.config['SECRET_KEY'] = "a poorly kept secret."
    csrf = csrf_token.CsrfTokenExt(app)
    csrf.init_app(app)
    app.client = app.test_client()

    @app.route('/foo', methods=['GET', 'POST'])
    def csrf_protected2():
        return 'protected'

    response = app.client.post("/foo", data={"name": "danny"})
    assert response.status_code == 200


