import pytest
import requests
from src.config import url
from src.error import AccessError,InputError
from tests.wrap_functions_test import *
import datetime 
from time import sleep
from datetime import *
import math

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

#test if the function working properly 
def test_proper_standup_active(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    wrap_standup_start(need_status_code,authid['token'],channelid['channel_id'],1)
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_standup_active(need_status_code,authid['token'],channelid['channel_id']) == {'is_active':True, 'time_finish':timestamp+1}
    sleep(2)
    assert wrap_standup_active(need_status_code,authid['token'],channelid['channel_id']) == {'is_active':False, 'time_finish':None}

# test if channel_id refer to a valid channel
def test_valid_channel_standup_active(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_standup_active(True,authid['token'], '-1') == InputError.code
    assert wrap_standup_active(True,authid['token'], '0') == InputError.code


# test when channel_id is valid, if the authorised user is a member of the channel
def test_auth_user_standup_active(clear_data):
    need_status_code = False
    authid1 = wrap_auth_register(need_status_code,"ahuahuag@gmail.com", "223344", "Ahua", "Hua")
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    channelid = wrap_channels_create(need_status_code,authid['token'], 'Jia', 'True')
    assert wrap_standup_active(True, authid1['token'], channelid['channel_id']) == AccessError.code