# A detection file is used to detect the channel_ join_ V1 (user_id, channel_id) and 
# channel_ invite_ V1 (user_id, channel_id, user_id) functions  consider its distinct "features".

# Written by Zhou Yanting (z5291515) on 19/10/2021

import pytest

from src.config import url
import json
import requests
from tests.wrap_functions_test import *
from src.error import *

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')
    
# To test channel_id does not refer to a valid channel
def test_unvalid_channel_id(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Add user1 as a owner in a unvalid channel
    assert wrap_channel_addowner(True, user1['token'], 123, user2['auth_user_id']) == InputError.code

# To test the case about user_id does not refer to a valid user
def test_unvalid_u_id(clear_data):
    need_status_code = False
    # Create one valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # Add unvalid user1 as a owner in a valid channel
    assert wrap_channel_addowner(True, user1['token'], Snake_id['channel_id'], 123) == InputError.code

# To check the case that user_id refers to a user who is not a member of the channel
def test_not_a_member(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    wrap_channels_create(need_status_code, user1['token'], "Snake", True)
    Snake_id2 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # Add a user who are not in channel
    assert wrap_channel_addowner(True, user1['token'], Snake_id2['channel_id'], user2['auth_user_id']) == InputError.code

# To Check the case about user who is already an owner of the channel
def test_already_owner(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    wrap_channel_join(False, user2['token'], Snake_id['channel_id'])
    # Add user2 as a owner
    wrap_channel_addowner(False, user1['token'], Snake_id['channel_id'], user2['auth_user_id'])
    # Add user2 as owner again and check whether as an input error
    assert wrap_channel_addowner(True, user1['token'], Snake_id['channel_id'], user2['auth_user_id']) == InputError.code

# Check the case that channel_id is valid and the authorised user does not have owner permissions in the channel
def test_no_permission(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    user3 = wrap_auth_register(need_status_code,"z5555555@unsw.edu.au", "333333", "Zhang", "Yicheng")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    wrap_channel_join(False, user2['token'], Snake_id['channel_id'])
    assert wrap_channel_addowner(True, user2['token'], Snake_id['channel_id'], user3['auth_user_id']) == AccessError.code

# Check the case that a global owner trys to add a non channel member
# It should raise access error
def test_global_owner_non_member_cant_addowner(clear_data):
    user1 = wrap_auth_register(False,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(False,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    user3 = wrap_auth_register(False,"z5555555@unsw.edu.au", "333333", "Zhang", "Yicheng")
    Snake_id = wrap_channels_create(False, user2['token'], "Snake", True)
    assert wrap_channel_addowner(True, user1['token'], Snake_id['channel_id'], user3['auth_user_id']) == AccessError.code

# Check the success case.
def test_valid_case1(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # user2 join into channel as a memeber
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])
    # Add user2 as a owner
    wrap_channel_addowner(need_status_code, user1['token'], Snake_id['channel_id'], user2['auth_user_id'])
    # Check channel infoemantion
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
        
