import pytest
import requests
from src.config import url
from src.error import AccessError,InputError
from tests.wrap_functions_test import *
import time
import datetime
from datetime import *
from time import sleep
import math

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

#test if the standup send function working properly 
def test_proper_standup_send(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    wrap_channels_create(need_status_code, authid['token'], 'i', True) 
    wrap_standup_start(need_status_code,authid['token'],channelid['channel_id'],1)
    wrap_standup_send(need_status_code, authid['token'], channelid['channel_id'], 'aaa') == {}
    wrap_standup_send(need_status_code, authid['token'], channelid['channel_id'], 'bbb')
    sleep(1)
    #standup send as message id 2 
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_channel_messages(need_status_code, authid['token'], channelid['channel_id'], 0) == {
        'end': -1,
        'messages': [
             {
                'message': 
                    'liyu: aaa\nliyu: bbb', 
                'message_id': 1,
                'time_created': pytest.approx(timestamp, abs=2),
                'u_id': 1,
                'reacts':[{
                    'react_id': 1,
                    'u_ids':[],
                    'is_this_user_reacted': False,
                }],
                'is_pinned': False
            }
        ], 
        'start': 0
    }




# test if channel_id refer to a valid channel
def test_valid_standup_send(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_channels_create(need_status_code, authid['token'], 'ab', True)
    wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_standup_send(True,authid['token'],'-1', 'hello') == InputError.code

# test id the length of message is over 1000 characters
def test_length_message_1000_standup_sends(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    need_status_code = True
    # when sending message with over 1000 characters or empty string
    assert wrap_standup_send(need_status_code, authid['token'], channelid['channel_id'], "") == InputError.code
    assert wrap_standup_send(need_status_code, authid['token'], channelid['channel_id'], "x" * 1001) == InputError.code

# test of there is a currently running standup in the channel --- check!!
def test_active_running_standup_send(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_channels_create(need_status_code, authid['token'], 'qq', True)
    wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    #no active standup, not running(not start)
    assert wrap_standup_send(True,authid['token'], channelid['channel_id'],'hello') == InputError.code
    
# test when channel_id is valid, if the authorised user is a member of the channel
def test_auth_user_standup_send(setup):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    wrap_channels_create(need_status_code, authid['token'], 'li', True)
    assert wrap_standup_send(True,authid1['token'], channelid['channel_id'],'hello') == AccessError.code