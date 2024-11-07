import requests
from src.config import url
from src.auth import generate_token
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

'''
this test should pass, cause auth login function received proper
email and password
'''
def test_proper_log_in(clear_data):
    wrap_auth_register(False,'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    assert wrap_auth_login(False,'bob@gmail.com', '123weAreFriends') == \
                            {'token': generate_token(1, 2), 'auth_user_id': 1}

'''
this test function tests when email entered does not belog to a user,
if an input error has raised
'''
def test_email_not_found(clear_data):
    assert wrap_auth_login(True,'hjk@gmail.com', '123weAreFriends') == InputError.code
    
    wrap_auth_register(True,'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    assert wrap_auth_login(True,'nus@gmail.com', '123weAreFriends') == InputError.code

'''
this test tests when user login with a wrong password, if an input error has raised
'''
def test_wrong_password(clear_data):
    wrap_auth_register(True,'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    assert wrap_auth_login(True,'bob@gmail.com', '123') == InputError.code
    assert wrap_auth_login(True,'bob@gmail.com', '') == InputError.code
