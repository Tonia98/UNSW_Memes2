import requests
from src.config import url
from src.auth import generate_token
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError
                                
@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# proper log out a valid user with valid session id, after log out token should 
# be invalid cause session id is invalid
def test_proper_log_out(clear_data):
    token_id = wrap_auth_register(False, 'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    wrap_auth_logout(False, token_id['token'])
    assert wrap_channels_create(True, token_id['token'], 'DODO', False) == AccessError.code

    token_id2 = wrap_auth_register(False, 'b@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    wrap_auth_logout(False, token_id2['token'])
    assert wrap_channels_create(True, token_id2['token'], 'DODO', False) == AccessError.code
# token format is not header.payload.verify signature
def test_invalid_token_format(clear_data):
    assert wrap_auth_logout(True, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9') == AccessError.code
    assert wrap_auth_logout(True, 'eyJhbGciOiJIUzI1N.iIsInR5cCI6IkpXVCJ9') == AccessError.code
    assert wrap_auth_logout(True, 'eyJhbGciOiJIUzI1N.iIsInR5cC.I6IkpXVCJ9') == AccessError.code

# after decode token, auth_user_id is invalid
def test_auth_user_id_not_found(clear_data):
    assert wrap_auth_logout(True, generate_token(1,1)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(2,2)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(3,2)) == AccessError.code

# after decode token, auth_user_id is valid, but session is not exsist 
def test_session_does_not_exsist(clear_data):
    wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    wrap_auth_register(True, 'bqwb@gmail.com', 'wqe21k0)!', 'Eva', 'Smith')
    wrap_auth_register(True, 'bookb@gmail.com', 'wqe21k0)!', 'Eva', 'Smith')
    assert wrap_auth_logout(True, generate_token(1,7)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(2,8)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(3,9)) == AccessError.code

# after decode token, auth_user_id is valid, session is exist, but session is not belong to auth_user 
def test_session_does_not_belong_to_user(clear_data):
    wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    wrap_auth_register(True, 'bqwb@gmail.com', 'wqe21k0)!', 'Eva', 'Smith')
    wrap_auth_register(True, 'bookb@gmail.com', 'wqe21k0)!', 'Eva', 'Smith')
    assert wrap_auth_logout(True, generate_token(1,2)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(2,3)) == AccessError.code
    assert wrap_auth_logout(True, generate_token(3,1)) == AccessError.code
