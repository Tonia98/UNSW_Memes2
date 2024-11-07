import pytest

from src.config import url
import json
import requests, math
from tests.wrap_functions_test import *
from datetime import datetime, timezone

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_no_notifications(clear_data):
    need_status_code = False
    # Create one valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")

    assert wrap_notifications_get(need_status_code, user1['token']) == {
        "notifications": []
    }


def test_adding_to_channel(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
  
    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
  
    assert wrap_notifications_get(need_status_code, user2['token']) == {
        "notifications": [
            {
                "channel_id": channel1["channel_id"],
                "dm_id": -1,
                "notification_message": "wujiameng added you to Snake"
            },
        ]
    }
    
# Test notification for adding to dm.
def test_adding_to_dm(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    assert wrap_notifications_get(need_status_code, user2['token']) == {
        "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm1["dm_id"],
                "notification_message": 'wujiameng added you to wujiameng, zhouyanting'
            },
        ]
    }

def test_tagged_channel(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    wrap_channels_create(need_status_code, user1['token'], "Wu", True)
    channel1 = wrap_channels_create(need_status_code,user2['token'], "Snake", True)
    assert wrap_channel_invite(True, user2['token'], channel1['channel_id'], user1['auth_user_id']) == 200
    msg1 = wrap_message_send(need_status_code, user2['token'], channel1["channel_id"], 'hi')
    wrap_message_send(need_status_code, user2['token'], channel1["channel_id"], '@world')
    # Message share with optional message tagging a user.
    wrap_message_share(need_status_code, user2['token'], msg1["message_id"], "hi @wujiameng", channel1["channel_id"], -1)
    
    assert wrap_notifications_get(need_status_code, user1['token']) == {
            "notifications": [
            {
                "channel_id": channel1["channel_id"],
                "dm_id": -1,
                "notification_message": "zhouyanting tagged you in Snake: hihi @wujiameng"
            },
            {
                "channel_id": channel1["channel_id"],
                "dm_id": -1,
                "notification_message": "zhouyanting added you to Snake"
            }
        ]
    }

def test_tagged_dm(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")
    
    wrap_dm_create(False, user1['token'], [])
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])
    msg1 = wrap_message_senddm(need_status_code, user2['token'], dm1["dm_id"], 'something')
    # Message share with optional message tagging a user.
    wrap_message_share(need_status_code, user2['token'], msg1["message_id"], "something @wujiameng", -1, dm1['dm_id'])
    
    assert wrap_notifications_get(need_status_code, user1['token']) == { 
            "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm1['dm_id'],
                "notification_message": "zhouyanting tagged you in wujiameng, zhouyanting: somethingsomething @"
            }
        ]
    }

def test_react_channel(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channel1 = wrap_channels_create(need_status_code, user1['token'], 'li', True)
    wrap_channels_create(need_status_code, user1['token'], '2323', True)
    wrap_message_send(need_status_code, user1['token'], channel1['channel_id'], 'sample testing')
    msg1 = wrap_message_send(need_status_code, user1['token'], channel1['channel_id'], 'something')
    assert wrap_message_react(need_status_code, user1['token'], msg1['message_id'], 1) == {}
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_channel_messages(need_status_code, user1['token'], channel1['channel_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'something',
            'time_created': timestamp,
            'reacts':[{
                'react_id': 1,
                'u_ids':[1],
                'is_this_user_reacted': True,
            }],
            'is_pinned': False
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'sample testing',
            'time_created': timestamp,
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1,
    }
    assert wrap_notifications_get(False, user1['token']) == {
        "notifications": [
            {
                "channel_id": channel1['channel_id'],
                "dm_id": -1,
                "notification_message": "liyu reacted to your message in li"
            }
        ]
    }



def test_react_dm(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    user2 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm1 = wrap_dm_create(need_status_code, user1['token'], [user2['auth_user_id']])
    wrap_dm_create(need_status_code, user2['token'], [])
    wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'something')
    msg1 = wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'sample message')
    assert wrap_message_react(need_status_code, user1['token'], msg1['message_id'], 1) == {}
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_dm_messages(need_status_code, user2['token'], dm1['dm_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'sample message',
            'time_created': timestamp,
            'reacts':[{
                'react_id': 1,
                'u_ids':[1],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'something',
            'time_created': timestamp,
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
            
        }],
        'start': 0,
        'end': -1,
    }
    assert wrap_notifications_get(False, user1['token']) == {
        "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm1['dm_id'],
                'notification_message': 'liyu reacted to your message in linglin, liyu'            
            }
        ]
    }


def test_tag_not_in_channel_dm(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)
    wrap_message_send(need_status_code, user1['token'], channel1["channel_id"], 'hi @zhouyanting')
    # Message share with optional message tagging a user.
    
    assert wrap_notifications_get(need_status_code, user1['token']) == {
            "notifications": []
    }

    dm1 = wrap_dm_create(need_status_code, user1['token'], []) 
    wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'hello @zhouyanting')
    assert wrap_notifications_get(need_status_code, user2['token']) == {
            "notifications": []
    }
