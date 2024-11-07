import pytest
import requests
from src.config import url
from src.error import AccessError,InputError
from tests.wrap_functions_test import *
import datetime 
from datetime import *
import time
import math

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

#test if the standup start function working properly
def test_proper_standup_start(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_standup_start(need_status_code,authid['token'],channelid['channel_id'],1) == {'time_finish':timestamp+1}

# test if channel_id refer to a valid channel
def test_valid_channel_standup_start(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_standup_start(True,authid['token'], '-1',1) == InputError.code

#test if the length is a negative integer
def test_length_negative_standup_start(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    assert wrap_standup_start(True,authid['token'],channelid['channel_id'], -1) == InputError.code


# test of there is a currently running standup in the channel
def test_active_running_standup_start(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True) 
    wrap_standup_start(need_status_code,authid['token'],channelid['channel_id'],2)
    assert wrap_standup_start(True,authid['token'],channelid['channel_id'],1) == InputError.code

# test when channel_id is valid, if the authorised user is a member of the channel
def test_auth_user_standup_start(clear_data):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    assert wrap_standup_start(True,authid1['token'], channelid['channel_id'],1) == AccessError.code