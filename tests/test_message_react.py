import pytest
import requests, math
from src.config import url
from tests.wrap_functions_test import *
from src.error import *
from datetime import datetime, timezone

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
def test_invalid_react_id(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid =wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 0) == InputError.code

def test_doble_reacting_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    need_status_code = True
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code

def test_doble_reacting_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    need_status_code = True
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code

def test_message_id_invalid_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    need_status_code = True
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code
    

def test_message_id_invalid_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "668843499", "yi", "lee")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    dmid1 = wrap_dm_create(need_status_code, authid2['token'], [authid3['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    messageid = wrap_message_senddm(need_status_code, authid2['token'], dmid1['dm_id'], 'sample message')
    need_status_code = True
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code
    
def test_success_react_single_channel_message(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'sample testing')
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == {}
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # test if user has successfully reacted to message
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'something',
            'time_created': pytest.approx(timestamp, abs=2),
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
            'time_created': pytest.approx(timestamp, abs=2),
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

def test_success_react_single_dm_message(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    wrap_dm_create(need_status_code, authid1['token'], [authid['auth_user_id']])
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'sample message')
    assert wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1) == {}
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # test if user has successfully reacted to message
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'sample message',
            'time_created': pytest.approx(timestamp, abs=2),
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
            'message': 'something',
            'time_created': pytest.approx(timestamp, abs=2),
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