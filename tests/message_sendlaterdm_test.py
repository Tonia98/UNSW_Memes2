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
    wrap_dm_create(True, auth['token'], [])

    auth2 = wrap_auth_register(False, "l@gmail.com", "112233", "li", "yu")
    wrap_dm_create(False, auth2['token'], [])
    
    return auth2['token']

def test_send_later_dm_correctly(clear_data):
    user2_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=2)
    expected_timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_sendlaterdm(True, user2_token, 2, "message1 send after 1s", expected_timestamp)
    sleep(2)
    ms = wrap_dm_messages(False, user2_token, 2, 0)
    # test if message has successfully sent later as scheduled in DM
    assert ms['messages'][0]['time_created'] == pytest.approx(expected_timestamp, abs=1)

def test_invalid_dm_id(clear_data):
    user2_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlaterdm(True, user2_token, 3, "m", exp_timestamp) == InputError.code
    
def test_dm_message_len_over_1000(clear_data):
    user2_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlaterdm(True, user2_token, 2, "m" * 1001, exp_timestamp) == InputError.code

def test_dm_time_sent_is_in_the_past(clear_data):
    user2_token = basic_function_set_up()

    dt = datetime.now() - timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlaterdm(True, user2_token, 2, "m", exp_timestamp) == InputError.code

def test_user_is_not_a_member_of_dm(clear_data):
    user2_token = basic_function_set_up()

    dt = datetime.now() + timedelta(seconds=1)
    exp_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    assert wrap_message_sendlaterdm(True, user2_token, 1, "m", exp_timestamp) == AccessError.code

