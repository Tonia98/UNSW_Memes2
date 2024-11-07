# A detection file is used to detect the dm_leave(token, dm_id)
# and functions  consider its distinct "features".
# Written by Zhou Yanting (z5291515) on 21/10/2021

import requests
from src.config import url
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError,InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_unvalid_DM(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    assert wrap_dm_leave(True, user1['token'], 123) == InputError.code

def test_unvalid_auth_id(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    wrap_dm_create(need_status_code, user1['token'], [])
    dm2 = wrap_dm_create(need_status_code, user1['token'], [])
    assert wrap_dm_leave(True, user2['token'], dm2['dm_id']) == AccessError.code

def test_valid_case(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    dm1 = wrap_dm_create(need_status_code, user1['token'], [user2['auth_user_id']]) 

    assert wrap_dm_details(need_status_code, user2['token'], dm1['dm_id']) ==  {
        'name': 'wujiameng, zhouyanting',
        'members': [
            {
                'u_id': user1['auth_user_id'],
                'email': '451842120@qq.com',
                'name_first': 'Wu',
                'name_last': 'Jiameng',
                'handle_str': 'wujiameng',
                'profile_img_url': url+'static/image.jpg'
            },
            {
                'u_id': user2['auth_user_id'],
                'email': 'z5291515@unsw.edu.au',
                'name_first': 'Zhou',
                'name_last': 'Yanting',
                'handle_str': 'zhouyanting',
                'profile_img_url': url+'static/image.jpg'
            },
        ]
    }
    wrap_dm_leave(need_status_code, user1['token'], dm1['dm_id'])
    assert wrap_dm_details(need_status_code, user2['token'], dm1['dm_id']) ==  {
        'name': 'wujiameng, zhouyanting',
        'members': [
            {
                'u_id': user2['auth_user_id'],
                'email': 'z5291515@unsw.edu.au',
                'name_first': 'Zhou',
                'name_last': 'Yanting',
                'handle_str': 'zhouyanting',
                'profile_img_url': url+'static/image.jpg'
            },
        ]
    }

