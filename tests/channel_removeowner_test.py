# A detection file is used to detect the channel_ removeowner_ V1 (token, channel_id) and 
# channel_ removeowner_ V1 (token, channel_id, u_id) functions  consider its distinct "features".

# Written by Zhou Yanting (z5291515) on 20/10/2021

import pytest

from src.channel import *
from src.channels import *
from src.other import *
from src.auth import *
from src.error import *
from src.config import url
import json
import requests
from tests.wrap_functions_test import *

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# To test the case that channel_id does not refer to a valid channel
def test_unvalid_channel(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # remove an user from a unvalid channel
    assert wrap_channel_removeowner(True, user1['token'], 123, user2['auth_user_id']) == InputError.code

# To test the case that u_id does not refer to a valid use
def test_unvalid_user(clear_data):
    need_status_code = False
    # Create one valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # make user2 as a member in channel but not an owner)
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    # remove an unvalid user from channel
    assert wrap_channel_removeowner(True, user1['token'], Snake_id['channel_id'], 3) == InputError.code

# To test the case that u_id refers to a user who is not an owner of the channel
def test_not_a_owner(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # make user2 as a member in channel but not an owner)
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    # remove a memeber using removeowner function
    assert wrap_channel_removeowner(True, user1['token'], Snake_id['channel_id'], user2['auth_user_id']) == InputError.code

# To test the case that u_id refers to a user who is currently the only owner of the channel
def test_only_owner(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # make user2 as a member in channel but not an owner)
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    # remove only owner in the channel
    assert wrap_channel_removeowner(True, user1['token'], Snake_id['channel_id'], user1['auth_user_id']) == InputError.code

# To test the case that channel_id is valid and the authorised user does not have owner permissions in the channel
def test_no_permission(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # make user2 as a member in channel but not an owner)
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    assert wrap_channel_removeowner(True, user2['token'], Snake_id['channel_id'], user1['auth_user_id']) == AccessError.code

# Check the case that a global owner trys to remove a non channel member
# It should raise access error
def test_global_owner_non_member_cant_addowner(clear_data):
    user1 = wrap_auth_register(False,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(False,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    user3 = wrap_auth_register(False,"z5555555@unsw.edu.au", "333333", "Zhang", "Yicheng")
    Snake_id = wrap_channels_create(False, user2['token'], "Snake", True)
    wrap_channel_addowner(False, user2['token'], Snake_id['channel_id'], user3['auth_user_id'])
    assert wrap_channel_removeowner(True, user1['token'], Snake_id['channel_id'], user3['auth_user_id']) == AccessError.code

# To test valid case
def test_valid_case1(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code, user1['token'], "Snake", True)
    # make user2 as a member in channel but not an owner)
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    # make user2 as a owner in channel
    wrap_channel_addowner(need_status_code, user1['token'], Snake_id['channel_id'], user2['auth_user_id'])
    # Check whether add successfully
    assert (wrap_channel_details(need_status_code, user1['token'], Snake_id['channel_id']) == 
        {
        'name': 'Snake',
        'owner_members': [  {'email': '451842120@qq.com',
                            'handle_str': 'wujiameng',
                            'name_first': 'Wu',
                            'name_last': 'Jiameng',
                            'u_id': 1,
                            'profile_img_url': url+'static/image.jpg'
                            },
                            {'email': 'z5291515@unsw.edu.au',
                            'handle_str': 'zhouyanting',
                            'name_first': 'Zhou',
                            'name_last': 'Yanting',
                            'u_id': 2,
                            'profile_img_url': url+'static/image.jpg'
                            }],
        'all_members': [    {'email': '451842120@qq.com',
                            'handle_str': 'wujiameng',
                            'name_first': 'Wu',
                            'name_last': 'Jiameng',
                            'u_id': 1,
                            'profile_img_url': url+'static/image.jpg'
                            },
                            {'email': 'z5291515@unsw.edu.au',
                            'handle_str': 'zhouyanting',
                            'name_first': 'Zhou',
                            'name_last': 'Yanting',
                            'u_id': 2,
                            'profile_img_url': url+'static/image.jpg'
                            }],
        'is_public': True,
        }
    )
    # remove user2 as an owner
    wrap_channel_removeowner(need_status_code, user1['token'], Snake_id['channel_id'], user2['auth_user_id'])
    assert (wrap_channel_details(need_status_code, user1['token'], Snake_id['channel_id']) == 
        {
        'name': 'Snake',
        'owner_members': [  {'email': '451842120@qq.com',
                            'handle_str': 'wujiameng',
                            'name_first': 'Wu',
                            'name_last': 'Jiameng',
                            'u_id': 1,
                            'profile_img_url': url+'static/image.jpg'
                            },],
        'all_members': [    {'email': '451842120@qq.com',
                            'handle_str': 'wujiameng',
                            'name_first': 'Wu',
                            'name_last': 'Jiameng',
                            'u_id': 1,
                            'profile_img_url': url+'static/image.jpg'
                            },
                            {'email': 'z5291515@unsw.edu.au',
                            'handle_str': 'zhouyanting',
                            'name_first': 'Zhou',
                            'name_last': 'Yanting',
                            'u_id': 2,
                            'profile_img_url': url+'static/image.jpg'
                            }],
        'is_public': True,
        }
    )

