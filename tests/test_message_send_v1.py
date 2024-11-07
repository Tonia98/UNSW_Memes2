from flask.globals import _request_ctx_stack
import pytest
from src.config import url
import requests
from datetime import datetime, timezone
from tests.wrap_functions_test import *
from src.error import *

'''
InputError 
- channel_id does not refer to a valid channel
- length of message is less than 1 or over characters
Access Error
- channel_id is valid and the autheroised user is not a member of the channel
'''
@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

# check if timestamp is working within a valid range (2 seconds)
def test_check_time_stamp_properly(setup):
    authid = wrap_auth_register(False, "liy@gmail.com", "112233", "li", "yu")
    wrap_channels_create(False, authid['token'], 'li', True)
    wrap_channels_create(False, authid['token'], 'li', True)
    dt = datetime.now()
    expected_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    wrap_message_send(False, authid['token'], 2, 'something')
    messages_info = wrap_channel_messages(False, authid['token'], 2, 0)
    curr_message = messages_info['messages'][0]
    assert abs(curr_message['time_created'] - expected_timestamp) < 2

# test channel_id does not refer to a valid channel
def test_channel_id_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    # input a random channel_id that is not valid with valid user_id
    need_status_code = True
    assert wrap_message_send(need_status_code, authid['token'], 5, 'something') == InputError.code    
    assert wrap_message_send(need_status_code, authid['token'], 9, 'sample message') == InputError.code

# test valid channel_id with invalid user
def test_channel_id_valid_user_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    need_status_code = True
    # input the incorrect user_id with a valid channel_id that the user is not belong to
    assert wrap_message_send(need_status_code, authid1['token'], channelid['channel_id'], 'sample message') == AccessError.code


def test_invalid_message_length(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    need_status_code = True
    # when sending message with over 1000 characters or empty string
    assert wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], "") == InputError.code
    assert wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], "x" * 1001) == InputError.code

# success returning message_id
def test_valid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    assert wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something') \
        == {
            'message_id': 1
        }
    assert wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'this') \
        == {
            'message_id': 2
        }

