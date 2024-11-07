from flask.globals import _request_ctx_stack
import pytest
from src.config import url
import requests, math
from datetime import timezone, datetime
from tests.wrap_functions_test import *
from src.error import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')



# test 1001 characters in message
def test_invalid_message_length(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_edit(need_status_code, authid['token'], message['message_id'], "x" * 1001) == InputError.code

def test_invalid_message_id(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_edit(need_status_code, authid1['token'], 3, 'sample edit') == InputError.code

#test empty input for editing a message
def test_empty_message_edit(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_edit(need_status_code, authid['token'], message['message_id'], "") 
    assert wrap_channel_messages(need_status_code, authid['token'],channelid['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

# editing message without raising any error
def test_success_editing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_edit(need_status_code, authid['token'], message['message_id'], "editted message") 
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'messages': [{
            'message_id': 1,
            'u_id': 1,
            'message': 'editted message',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1
    }

# test accesserror for not having owner permission 
def test_no_owner_per(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channel_join(need_status_code, authid1['token'], channelid['channel_id'])
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_edit(need_status_code, authid1['token'], message['message_id'], 'editted message') == AccessError.code

# test accesserror for invalid user editing message
def test_not_send_by_valid_user(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "7892462", "lyn", "jiang")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_edit(need_status_code, authid2['token'], message['message_id'], 'editted message') == AccessError.code

# test valid dm_id and user editing messages
def test_success_dm_editing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    message = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a message from the owner")
    assert wrap_message_edit(need_status_code, authid['token'], message['message_id'], "editted message") == {}
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [{
            'message_id': 1,
            'u_id': 1,
            'message': 'editted message',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1
    }
# test edit with an empty string for the only message in dm
def test_success_dm_editing_empty(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    message = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a message from the owner")
    wrap_message_edit(need_status_code, authid['token'], message['message_id'], "")
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1
    }

# test editing message with message send to channel and dm
def test_editing_multiple(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channel_join(need_status_code, authid1['token'], channelid['channel_id'])
    # create a dm 
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    # send a message to dm
    wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'Sample')
    # send messages to channel
    message = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_send(need_status_code, authid1['token'], channelid['channel_id'], 'sample message in the channel')
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'overloading server!!!')
    # edit message in channel
    wrap_message_edit(need_status_code, authid['token'], message['message_id'], "server is extremely overloading!") 
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'messages': [{
            'message_id': 4,
            'u_id': 1,
            'message': 'overloading server!!!',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        },
        {
            'message_id': 3,
            'u_id': 2,
            'message': 'sample message in the channel',
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
            'message': 'server is extremely overloading!',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1
    }

def test_invalid_dm_editing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "7892462", "lyn", "jiang")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    message = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a message from the owner")
    need_status_code = True
    # invalid user id with valid message id requesting to edit message in dm
    wrap_message_edit(need_status_code, authid2['token'], message['message_id'], "") == AccessError.code

def test_invalid_messageid_dm_editing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], "This is a message from the owner")
    need_status_code = True
    # valid user id with invalid message id requesting to edit message in dm
    wrap_message_edit(need_status_code, authid['token'], 2, "") == InputError.code