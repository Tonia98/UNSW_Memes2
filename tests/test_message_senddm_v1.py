import pytest
import requests
from src.config import url
from tests.wrap_functions_test import *
from src.error import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')


# test dm_id does not refer to a valid dm
def test_dm_id_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    # input a random dm_id that is not valid with valid user_id
    need_status_code = True
    assert wrap_message_senddm(need_status_code, authid['token'], 5, 'something') == InputError.code    
    assert wrap_message_senddm(need_status_code, authid['token'], 9, 'sample message') == InputError.code

# test valid dm_id with invalid user
def test_dm_id_valid_user_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "559988", "lyn", "jiang")
    authid3 = wrap_auth_register(need_status_code, "cly@gmail.com", "5007428", "anna", "huang")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_dm_create(need_status_code, authid['token'], [authid2['auth_user_id']])
    need_status_code = True
    # input the incorrect user_id with a valid dm_id that the user is not belong to
    assert wrap_message_senddm(need_status_code, authid3['token'], dm['dm_id'], 'sample message') == AccessError.code


def test_invalid_message_length(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    need_status_code = True
    # when sending message with over 1000 characters or empty string
    assert wrap_message_senddm(need_status_code, authid1['token'], dm['dm_id'], "") == InputError.code
    assert wrap_message_senddm(need_status_code, authid1['token'], dm['dm_id'], "x" * 1001) == InputError.code

# success returning message_id
def test_valid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    assert wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'something') \
        == {
            'message_id': 1
        }
    assert wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'this') \
        == {
            'message_id': 2
        }

    