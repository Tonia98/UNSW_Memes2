from flask.globals import _request_ctx_stack
import pytest, requests, math
from src.config import url
from tests.wrap_functions_test import *
from src.error import *
from datetime import datetime, timezone

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')


def test_invalid_channelid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_remove(need_status_code, authid['token'], 2) == InputError.code

# remove a message when there's only one message exist in data_store
def test_working(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_remove(need_status_code, authid['token'], message['message_id'])
    # returns an empty message list
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }


def test_invalid_user_removing_message(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    # invalid user attempting to remove a message from channel
    assert wrap_message_remove(need_status_code, authid1['token'], message['message_id']) == AccessError.code
    

def test_no_owner_per(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channel_join(need_status_code, authid1['token'], channelid['channel_id'])
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'Hellooooo')
    need_status_code = True
    # removing a message with valid message_id from a user that does not have owner permission
    assert wrap_message_remove(need_status_code, authid1['token'], message['message_id']) == AccessError.code

def test_not_send_by_valid_user(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    # removing a message with valid message_id from an invalid user
    assert wrap_message_remove(need_status_code, authid1['token'], message['message_id']) == AccessError.code

def test_success_dm_remove(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    message = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a message from the owner")
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a direct message from the owner")
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "Hello World")
    # remove least recent message from dm 
    wrap_message_remove(need_status_code, authid['token'], message['message_id'])
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # returns other messages existing in dm
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [{
            'message_id': 3,
            'u_id': 1,
            'message': 'Hello World',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        },
        {
            'message_id': 2,
            'u_id': 1,
            'message': 'This is a direct message from the owner',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }
        ],
        'start': 0,
        'end': -1
    }