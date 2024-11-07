# A detection file is used to detect the channel_ join_ V1 (token, channel_id) and 
# channel_ invite_ V1 (token, channel_id, u_id) functions  consider its distinct "features".

# Written by Zhou Yanting (z5291515) on 26/9/2021

import pytest

from src.config import url
import json
import requests
from tests.wrap_functions_test import *
from src.error import *

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_input_error_case(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    # Create a channel
    Snake_id = wrap_channels_create(need_status_code, user1['token'], "Snake", True)
    # Check whether a channel is built successfully
    assert(wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': Snake_id['channel_id'],
                'name': 'Snake',
            },
        ]
    })
    # Join a valid user into a invalid channel
    assert wrap_channel_join(True, user2['token'], 123) == InputError.code

    # Check whether user is join or not
    assert(wrap_channels_list(False, user2['token']) == {'channels': []})


def test_join_valid(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "11111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")

    # Create a channel
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # Join user2 into channel
    wrap_channel_join(need_status_code, user2['token'], Snake_id['channel_id'])

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


def test_AccessError(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "11111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")

    # Create a channel that is not public
    Snake_id = wrap_channels_create(need_status_code,user1['token'], "Snake", False)

    # the authorised user is not already a channel member and is not a global owner
    assert wrap_channel_join(True, user2['token'], Snake_id['channel_id']) == AccessError.code
    
    # Check whether user is join or not
    assert(wrap_channels_list(False, user2['token']) == {'channels': []})


def test_join_error(clear_data):
    # token(1) doesn't exist
    need_status_code = False
    assert wrap_channel_join(True, 1, 1) == AccessError.code

    user1 = wrap_auth_register(False, "451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(False, "z5291515@unsw.edu.au", "22222222", "Zhou", "Yanting")
    
    # channel(123) doesn't exist
    assert wrap_channel_join(True, user1['token'], 1) == InputError.code
        
    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    # token(1) cant't join channel(1)
    # as token(1) is already in channel(1)
    assert wrap_channel_join(True, user1['token'], 1) == InputError.code
    
    # token(2) joins channel(1) successfully
    wrap_channel_join(need_status_code, user2['token'], channel1['channel_id'])
    assert(wrap_channels_list(False, user2['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'Snake',
            },
        ]
    })
    channel2 = wrap_channels_create(need_status_code,user1['token'], "Tetris", False)
     # token(2) can't joins channel(2) because its private
    assert wrap_channel_join(True, user2['token'], channel2['channel_id']) == AccessError.code
        
    channel3 = wrap_channels_create(need_status_code,user2['token'], "Pacman", False)
    # token(1) joins channel(3)(private) successfully 
    # because token(1) is global owner
    wrap_channel_join(need_status_code, user1['token'], channel3['channel_id'])
    assert(wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'Snake',
            },
            {
                'channel_id': channel2['channel_id'],
                'name': 'Tetris',
            },
            {
                'channel_id': channel3['channel_id'],
                'name': 'Pacman',
            },
        ]
    })

