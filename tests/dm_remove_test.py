import pytest
import requests
from requests.models import codes
from tests.wrap_functions_test import *
from src.config import url
from src.error import AccessError
from src.error import InputError
#from src.data_store import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
# test the dm_details function working properly with single dm and single user
def test_proper_details_single(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    wrap_dm_create(need_status_code, authid['token'], [])
    dm2 = wrap_dm_create(need_status_code, authid['token'], [])
    wrap_dm_remove(need_status_code, authid['token'], dm2['dm_id'])
    assert wrap_dm_details(True, authid['token'], dm2['dm_id']) == InputError.code


# test if dm_id refer to a valid dm
def test_valid_dm_remove(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_dm_remove(True,authid['token'], '-1') == InputError.code
    assert wrap_dm_remove(True,authid['token'], '0') == InputError.code
    


# test when dm_id is valid, if the authorised user is not a creator of the dm
def test_auth_user_remove(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    dmid = wrap_dm_create(need_status_code,authid1['token'], [authid['auth_user_id']])
    wrap_dm_remove(need_status_code, authid['token'], dmid['dm_id']) == AccessError.code
