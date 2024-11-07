# A detection file is used to detect the channel_ leave_ V1 (token, channel_id) and 
# channel_ invite_ V1 (token, channel_id, u_id) functions  consider its distinct "features".

# Written by Zhou Yanting (z5291515) on 20/10/2021

import pytest

from tests.wrap_functions_test import *
from src.config import url
import json
import requests
from src.error import *

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')


def test_unvalid_channel(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    assert wrap_channel_leave(True, user1['token'], 123) == InputError.code

def test_not_member(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code, user1['token'], "Snake", True)
    assert wrap_channel_leave(True, user2['token'], Snake_id['channel_id']) == AccessError.code

def test_valid_case1(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    # Create a channel
    Snake_id = wrap_channels_create(need_status_code, user1['token'], "Snake", True)
    assert(wrap_channels_list(need_status_code, user1['token']) == {
        'channels': [
            {
                'channel_id': Snake_id['channel_id'],
                'name': 'Snake',
            },
        ]
    })
    wrap_channel_leave(need_status_code, user1['token'], Snake_id['channel_id'])

    assert(wrap_channels_list(need_status_code, user1['token']) == {
        'channels': []})
