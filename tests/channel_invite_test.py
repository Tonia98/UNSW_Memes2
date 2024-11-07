# A detection file is used to detect the channel_ join_ V1 (token, channel_id) and 
# channel_ invite_ V1 (token, channel_id, u_id) functions  consider its distinct "features".

# Written by Zhou Yanting (z5291515) on 26/9/2021

import pytest

from src.config import url
import json
import requests
from tests.wrap_functions_test import *
from src.error import *
from src.config import url

def test_input_error_case2():
    requests.delete(url + 'clear/v1')
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code, user1['token'], "Snake", False)
    # Check whether a channel is built successfully
    assert(wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': Snake_id['channel_id'],
                'name': 'Snake',
            },
        ]
    })
    # Invite user2 into a invalid channel
    
    assert wrap_channel_invite(True, user1['token'], 123, user2['auth_user_id']) == InputError.code
    
    # Check whether user2 is join or not
    assert(wrap_channels_list(False, user2['token']) == {'channels': []})


def test_invite_valid():
    requests.delete(url + 'clear/v1')
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "11111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")

    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", False)
    # Join user2 into channel
    wrap_channel_invite(False, user1['token'], Snake_id['channel_id'], user2['auth_user_id'])

    # CHeck whether a channel is built successfully
    assert(wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': Snake_id['channel_id'],
                'name': 'Snake',
            },
        ]
    })
    
    assert(wrap_channels_list(False, user2['token']) == {
        'channels': [
            {
                'channel_id': Snake_id['channel_id'],
                'name': 'Snake',
            },
        ]
    })

def test_errors():
    requests.delete(url + 'clear/v1')
    need_status_code = False
    # token(1) doesn't exist
    assert wrap_channel_invite(True, 1, 123, 2) == AccessError.code
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")
    
    # channel(123) doesn't exist
    assert wrap_channel_invite(True, user1['token'], 123, user2['auth_user_id']) == InputError.code
    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", False)
    
    # token(2) tries to invite u_id(1) into channel(1)
    # but token(2) is not in channel(1)
    assert wrap_channel_invite(True, user2['token'], channel1['channel_id'], user1['auth_user_id']) == AccessError.code
        
    # token(1) invite u_id(2) successfully into channel(1)
    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    assert(wrap_channels_list(False, user2['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'Snake',
            },
        ]
    })
     
     # token(1) invite u_id(2) into channel(1)
     # but u_id(2) already exist in channel(1)
    assert wrap_channel_invite(True, user1['token'], channel1['channel_id'], user2['auth_user_id']) == InputError.code
    
    # token(1) invite u_id(3) into channel(1)
    # but u_id(3) doesn't exist
    assert wrap_channel_invite(True, user1['token'], channel1['channel_id'], 3) == InputError.code 
        
    
def test_AccessError():
    requests.delete(url + 'clear/v1')
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "11111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")
    user3 = wrap_auth_register(need_status_code,"z1234567@unsw.edu.au", "33333333", "Ren", "yan")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", False)

    # to check the authorised user is not a member of the channel 
    assert wrap_channel_invite(True, user2['token'], Snake_id['channel_id'], user3['auth_user_id']) == AccessError.code

    # Check whether user2 is join or not
    assert(wrap_channels_list(False, user3['token']) == {'channels': []})

