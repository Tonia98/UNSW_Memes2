import pytest
from tests.wrap_functions_test import *
from src.error import *
from src.config import url
import requests, math
from datetime import datetime, timezone

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
# Assumptions : all the input format for auth_register and channels_create are correct

# assume start is greater than number of message for this testing only 
def test_start_greater_than_messages(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    need_status_code = True
    assert wrap_channel_messages(need_status_code, authid['token'],channelid1['channel_id'], 50) == InputError.code


# test channel_id does not refer to a valid channel
def test_channel_id_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    # input a random channel_id that is not valid with valid user_id
    need_status_code = True 
    assert wrap_channel_messages(need_status_code, authid['token'], 5, 0) == InputError.code
    assert wrap_channel_messages(need_status_code, authid['token'], 9, 0) == InputError.code

# test valid channel_id with invalid user
def test_channel_id_valid_user_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    need_status_code = True
    # input the incorrect user_id with a valid channel_id that the user is not belong to
    assert wrap_channel_messages(need_status_code, authid1['token'],channelid['channel_id'], 0) == AccessError.code

# test all inputs are correct as required
def test_empty(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    # this input will return a empty list for messages as no messages are in data_store
    assert wrap_channel_messages(need_status_code, authid['token'],channelid['channel_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

def test_existing_messages(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'this is a message by the first person in the channel')
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # this input will return a empty list for messages as no messages are in data_store
    assert wrap_channel_messages(need_status_code, authid['token'],channelid['channel_id'], 0) == {
        'messages': [
            {'message_id': 1,
            'u_id': 1,
            'message': 'this is a message by the first person in the channel',
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


def test_over_50_message_existing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    i = 0
    while i < 50:
        wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'Hello World')
        i += 1
    result = wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0)
    assert result['start'] == 0
    assert result['end'] == 50
