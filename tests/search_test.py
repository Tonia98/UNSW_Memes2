import pytest

from src.config import url
import json
import requests
from tests.wrap_functions_test import *
from src.error import *
from datetime import datetime, timezone
from time import sleep
import math

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_channel_message(clear_data):
    need_status_code = False
    # Create one valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "222222", "Zhou", "Yanting")

    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    sleep(1)
    dt = datetime.now()
    msg1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    assert wrap_message_send(need_status_code, user1['token'], channel1['channel_id'], 'something') == {
            'message_id': 1
        }
    assert wrap_message_send(need_status_code, user1['token'], channel1['channel_id'], 'this') == {
            'message_id': 2
        }
    assert wrap_search(need_status_code, user1['token'], "some") == [
        {
        'message_id': 1,
        'u_id': 1,
        'message': 'something',
        'time_created': pytest.approx(msg1_time, abs=2),
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
        'is_pinned': False
        }
    ]

def test_dm_message(clear_data):
    need_status_code = False
    
    # Create one valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "222222", "Zhou", "Yanting")

    sleep(1)
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    sleep(1)
    dt = datetime.now()
    msg1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'something') 
    wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'this') 
  
    assert wrap_search(need_status_code, user1['token'], "some") == [
        {
        'message_id': 1,
        'u_id': 1,
        'message': 'something',
        'time_created': pytest.approx(msg1_time, abs=2),
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
        'is_pinned': False
        }
    ]

def test_invalid_string(clear_data):
    need_status_code = False
    # create a new user
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    # create a new channel
    wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    assert wrap_search(True, user1['token'], "") ==  InputError.code
