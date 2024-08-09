from http import HTTPStatus

import pytest
from fastapi.exceptions import HTTPException
from jwt import decode

from madr.security import create_access_token, get_current_user, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert decoded['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_without_sub():
    token = create_access_token({'test': 'test'})
    with pytest.raises(HTTPException):
        get_current_user(token=token)


def test_get_current_user_pyjwterror(session):
    with pytest.raises(HTTPException):
        get_current_user(token='lalala', session=session)
