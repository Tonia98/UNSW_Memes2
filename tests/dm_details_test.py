import requests
from src.config import url
import pytest
from src.error import AccessError,InputError
from tests.wrap_functions_test import *
                
@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

# test the dm_details function working properly with single dm and single user
def test_proper_details_single(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    dm1 = wrap_dm_create(need_status_code, authid['token'], [])
    assert wrap_dm_details(need_status_code, authid['token'], dm1['dm_id']) == {
        'name': 'jiacheng',
        'members': [
            {
                'u_id': authid['auth_user_id'],
                'email': 'jiacheng@gmail.com',
                'name_first': 'Jia',
                'name_last': 'Cheng',
                'handle_str': 'jiacheng',
                'profile_img_url': url+'static/image.jpg'
            }
        ]
    }
def test_proper_details_multiples(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    authid2 = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    dm1 = wrap_dm_create(need_status_code, authid1['token'], [authid2['auth_user_id']]) 

    assert wrap_dm_details(need_status_code, authid2['token'], dm1['dm_id']) ==  {
        'name': 'jiacheng, wujiameng',
        'members': [
            {
                'u_id': authid1['auth_user_id'],
                'email': '451842120@qq.com',
                'name_first': 'Wu',
                'name_last': 'Jiameng',
                'handle_str': 'wujiameng',
                'profile_img_url': url+'static/image.jpg'
            },
            {
                'u_id': authid2['auth_user_id'],
                'email': 'jiacheng@gmail.com',
                'name_first': 'Jia',
                'name_last': 'Cheng',
                'handle_str': 'jiacheng',
                'profile_img_url': url+'static/image.jpg'
            },
        ]
    }


# test if dm_id refer to a valid dm
def test_valid_dm_details(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_dm_details(True,authid['token'], '-1') == InputError.code
    assert wrap_dm_details(True,authid['token'], '0') == InputError.code
    


# test when dm_id is valid, if the authorised user is a member of the dm
def test_auth_user_details(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    dmid = wrap_dm_create(need_status_code,authid['token'], [])
    wrap_dm_details(True,authid1['token'], dmid['dm_id']) == AccessError.code
