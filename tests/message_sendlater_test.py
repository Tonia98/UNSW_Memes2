import requests
from src.config import url
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError
from datetime import datetime, timezone, timedelta
from time import sleep
import math

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def basic_function_set_up():
    auth = wrap_auth_register(False, "liy@gmail.com", "112233", "li", "yu")
    wrap_channels_create(False, auth['token'], 'li', True)
    
    auth2 = wrap_auth_register(False, "l@gmail.com", "112233", "li", "yu")
    wrap_channels_create(False, auth2['token'], 'li', True)
    
    return auth['token']

def test_message_correctly_sendlater(clear_data):
    user1_token = basic_function_set_up()
    wrap_channel_join(True, user1_token, 2)

    dt = datetime.now() + timedelta(seconds=2)
    expected_timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_sendlater(True, user1_token, 2, "message1 send after 1s", expected_timestamp)
    sleep(2)
    ms = wrap_channel_messages(False, user1_token, 2, 0)
    # test if message has successfully sent later as scheduled
    assert ms['messages'][0]['time_created'] == pytest.approx(expected_timestamp, abs=1)

def test_invalid_channel_id(clear_data):
    user1_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlater(True, user1_token, 3, "message1 send after 1s",\
                                  exp_timestamp) == InputError.code
                            
def test_message_len_is_over_1000(clear_data):
    user1_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlater(True, user1_token, 1, "m" * 1001, exp_timestamp) == InputError.code
                                
def test_message_sent_time_is_in_the_past(clear_data):
    user1_token = basic_function_set_up()

    dt = datetime.now() - timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlater(True, user1_token, 1, "message1 send ",\
                                  exp_timestamp) == InputError.code
                      
def test_user_is_not_a_member_of_channel(clear_data):
    user1_token = basic_function_set_up()
    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlater(True, user1_token, 2, "m"*1001, exp_timestamp) == AccessError.code
    
    

