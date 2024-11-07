import requests
from src.config import url
import pytest
from src.error import AccessError,InputError
from tests.wrap_functions_test import *
                
@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

# test the channel_details function working properly with single channel and single user
def test_proper_details_single(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'Jia', True)
    assert wrap_channel_details(need_status_code,authid['token'], channelid['channel_id']) == {
        'name': 'Jia',
        'owner_members': [
            {
                'u_id': authid['auth_user_id'],
                'email': 'jiacheng@gmail.com',
                'name_first': 'Jia',
                'name_last': 'Cheng',
                'handle_str': 'jiacheng',
                'profile_img_url': url+'static/image.jpg'
            },
        ],
        'all_members': [
            {
                'u_id': authid['auth_user_id'],
                'email': 'jiacheng@gmail.com',
                'name_first': 'Jia',
                'name_last': 'Cheng',
                'handle_str': 'jiacheng',
                'profile_img_url': url+'static/image.jpg'
            },
        ],
        'is_public': True
    }

def test_proper_details_multiples(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    authid2 = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid1 = wrap_channels_create(need_status_code,authid1['token'], 'Jia', True)
    wrap_channel_invite(need_status_code,authid1['token'],channelid1['channel_id'],authid2['auth_user_id']) 

    assert wrap_channel_details(need_status_code,authid2['token'],channelid1['channel_id']) ==  {
        'name': 'Jia',
        'owner_members': [
            {
                'u_id': authid1['auth_user_id'],
                'email': '451842120@qq.com',
                'name_first': 'Wu',
                'name_last': 'Jiameng',
                'handle_str': 'wujiameng',
                'profile_img_url': url+'static/image.jpg'
            },
        ],
        'all_members': [
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
        ],
        'is_public': True
    }


# test if channel_id refer to a valid channel
def test_valid_channel_details(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_channel_details(True,authid['token'], '-1') == InputError.code
    assert wrap_channel_details(True,authid['token'], '0') == InputError.code
    


# test when channel_id is valid, if the authorised user is a member of the channel
def test_auth_user_details(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    wrap_channel_details(True,authid1['token'], channelid['channel_id']) == AccessError.code


