import pytest
import requests, math
from src.config import url
from tests.wrap_functions_test import *
from src.error import *
from datetime import datetime, timezone


@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')


def test_invalid_channel_id_and_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid =wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], '', 2, 2) == InputError.code 

def test_both_channel_dm_negative_1(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid =wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], '', -1, -1) == InputError.code 

def test_not_sharing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_send(need_status_code, authid1['token'], channelid1['channel_id'], 'other thing')
    wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], '', channelid1['channel_id'], -1) == AccessError.code 


def test_message_over_length(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], "x" * 1001, channelid['channel_id'], -1) == InputError.code 
    
def test_og_message_id_invalid_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    wrap_message_send(need_status_code, authid1['token'], channelid1['channel_id'], 'something')
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'sample message')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid1['token'], messageid['message_id'], 'shared message', channelid1['channel_id'], -1) == InputError.code

def test_og_message_id_invalid_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "668843499", "yi", "lee")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    dmid1 = wrap_dm_create(need_status_code, authid2['token'], [authid3['auth_user_id']])
    dmid2 = wrap_dm_create(need_status_code, authid['token'], [authid3['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    messageid = wrap_message_senddm(need_status_code, authid2['token'], dmid1['dm_id'], 'sample')
    wrap_message_senddm(need_status_code, authid3['token'], dmid1['dm_id'], 'sample message')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], 'shared message', -1, dmid2['dm_id']) == InputError.code
    
def test_invalid_message_id_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], 2, 'shared message', channelid['channel_id'], -1) == InputError.code

def test_invalid_message_id_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "668843499", "yi", "lee")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dm = wrap_dm_create(need_status_code, authid1['token'], [authid3['auth_user_id']])
    wrap_dm_create(need_status_code, authid['token'], [authid3['auth_user_id']])
    dm1 = wrap_dm_create(need_status_code, authid1['token'], [authid2['auth_user_id']])
    wrap_message_senddm(need_status_code, authid1['token'], dm['dm_id'], 'something')
    wrap_message_senddm(need_status_code, authid2['token'], dm1['dm_id'], 'sample')
    wrap_message_senddm(need_status_code, authid2['token'], dm1['dm_id'], 'sample message')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid1['token'], 4, 'shared message', -1, dm1['dm_id']) == InputError.code



def test_valid_ids_invalid_user_access_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_send(need_status_code, authid1['token'], channelid1['channel_id'], 'sample message')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], 'shared message', channelid1['channel_id'], -1) == AccessError.code
    
    
def test_valid_ids_invalid_user_access_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "668843499", "yi", "lee")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    dmid1 = wrap_dm_create(need_status_code, authid2['token'], [authid3['auth_user_id']])
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    wrap_message_senddm(need_status_code, authid1['token'], dmid1['dm_id'], 'sample message')
    need_status_code = True
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], 'shared message', -1, dmid1['dm_id']) == AccessError.code

def test_sccess_empty_string_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    wrap_channel_join(need_status_code, authid1['token'], channelid['channel_id'])
    wrap_message_send(need_status_code, authid1['token'], channelid['channel_id'], 'sample')
    messageid = wrap_message_send(need_status_code, authid1['token'], channelid['channel_id'], 'something')
    assert wrap_message_share(need_status_code, authid1['token'], messageid['message_id'], ' is something', channelid1['channel_id'], -1) == {
        'shared_message_id': 3
        }
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # check if the user has successfully shared the message
    assert wrap_channel_messages(need_status_code, authid1['token'], channelid1['channel_id'], 0) == {
        'messages': [{
            'message_id': 3,
            'u_id': 2,
            'message': 'something is something',
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
    
def test_sccess_empty_string_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dmid1 = wrap_dm_create(need_status_code, authid['token'], [authid3['auth_user_id']])
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid1['dm_id'], 'sample message')
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], ' is something', -1, dmid['dm_id']) == {
        'shared_message_id': 3
        }
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # check if the user has successfully shared the message
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [{
            'message_id': 3,
            'u_id': 1,
            'message': 'sample message is something',
            'time_created': timestamp,
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
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
        }
        ],
        'start': 0,
        'end': -1,
    
    }

def test_sharing_from_dm_to_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], ' extra', channelid['channel_id'], -1) == {
        'shared_message_id': 2
    }
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # check if the user has successfully shared the message
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'something extra',
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
    
def test_sharing_from_channel_to_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    assert wrap_message_share(need_status_code, authid['token'], messageid['message_id'], ' extra', -1, dmid['dm_id']) == {
        'shared_message_id': 2
    }
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # check if the user has successfully shared the message
    assert wrap_dm_messages(need_status_code, authid['token'], dmid['dm_id'], 0) == {
        'messages': [{
            'message_id': 2,
            'u_id': 1,
            'message': 'something extra',
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
