from http import HTTPStatus

from passlib.apps import django_context
from flask_security.utils import get_hmac

from .utils import login
from ..users.models import User


def django_fixture():
    return {
        "fields": {
            "email": "doe@example.com",
            "password": "pbkdf2_sha256$10000$c526TVwJZ5U5$QSM9+Da1IiIILNj4Z8B8q9RRH4Y7L8SrVM5lfU9FdZc=",  # NOQA
        }
    }


def test_can_verify_django_password():
    assert django_context.verify('vincent',
                                 django_fixture()['fields']['password'])


def test_can_verify_django_and_flask_password(app, user):
    context = app.extensions['security'].pwd_context
    assert context.verify(get_hmac('password'), user.password)
    assert context.verify('vincent', django_fixture()['fields']['password'])


def test_login_with_django_password(client):
    data = django_fixture()['fields']
    User.objects.create(email=data['email'], password=data['password'])
    user = User.objects.get(email=data['email'])
    login(client, user['email'], 'vincent')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK


def test_login_with_django_password_updates_password_to_bcrypt(client):
    data = django_fixture()['fields']
    User.objects.create(email=data['email'], password=data['password'])
    user = User.objects.get(email=data['email'])
    assert user.password == data['password']
    login(client, user['email'], 'vincent')
    user.reload()
    assert user.password != data['password']
    assert user.password.startswith('$2b$12$')
    login(client, user['email'], 'vincent')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK
