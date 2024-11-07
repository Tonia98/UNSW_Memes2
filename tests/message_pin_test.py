import requests
from src.config import url
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# this function create 2 users, 2 channels, 2 dms
# then send 1 message to each channel each dm
def basic_function_set_up():
    auth = wrap_auth_register(False, "liy@gmail.com", "112233", "li", "yu")
    auth2 = wrap_auth_register(False, "dd@gmail.com", "112233", "li", "yu")

    wrap_channels_create(False, auth['token'], 'li', True)
    wrap_channels_create(False, auth2['token'], 'li', True)
    wrap_dm_create(False, auth['token'], [])
    wrap_dm_create(False, auth2['token'], [])

    wrap_message_send(False, auth['token'], 1, 'message id: 1')
    wrap_message_send(False, auth2['token'], 2, 'message id: 2')

    wrap_message_senddm(False, auth['token'], 1, 'message id: 3')
    wrap_message_senddm(False, auth2['token'], 2, 'message id: 4')

    return (auth['token'], auth2['token'])

def get_channel_or_dm_message(user1_token, user2_token):
    channel1_m = wrap_channel_messages(False, user1_token, 1, 0)
    channel2_m = wrap_channel_messages(False, user2_token, 2, 0)
    dm1_m = wrap_dm_messages(False, user1_token, 1, 0)
    dm2_m = wrap_dm_messages(False, user2_token, 2, 0)
    return (channel1_m, channel2_m, dm1_m, dm2_m)

def test_pin_message_successfull(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    # in channel, the message id of the first message send in the second channel is 1
    wrap_message_pin(False, user1_token, 1)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    assert channel1_m['messages'][0]['is_pinned'] == True
    assert channel2_m['messages'][0]['is_pinned'] == False
    wrap_channel_join(False, user1_token, 2)
    wrap_message_pin(False, user1_token, 2)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    assert channel2_m['messages'][0]['is_pinned'] == True
    
    # in dm, the message id of the first(oldest) message send in the second dm is 3
    wrap_message_pin(False, user1_token, 3)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    assert dm1_m['messages'][0]['is_pinned'] == True
    assert dm2_m['messages'][0]['is_pinned'] == False
    wrap_message_pin(False, user2_token, 4)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    assert dm2_m['messages'][0]['is_pinned'] == True

def test_invalid_message_id_within_a_channel_or_DM_that_the_authorised_user_has_joined(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    # in channels
    assert wrap_message_pin(True, user1_token, 5) == InputError.code
    assert wrap_message_pin(True, user2_token, 1) == InputError.code
    
    # in dms
    assert wrap_message_pin(True, user2_token, 3) == InputError.code
    assert wrap_message_pin(True, user1_token, 4) == InputError.code
    assert wrap_message_pin(True, user2_token, 5) == InputError.code

def test_message_already_pinned(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    # in channels
    wrap_channel_join(False, user1_token, 2)
    wrap_message_pin(False, user1_token, 2)
    assert wrap_message_pin(True, user2_token, 2) == InputError.code
    assert wrap_message_pin(True, user1_token, 2) == InputError.code

    # in dms
    wrap_message_pin(False, user1_token, 3)
    assert wrap_message_pin(True, user1_token, 3) == InputError.code
    wrap_message_pin(False, user2_token, 4)
    assert wrap_message_pin(True, user2_token, 4) == InputError.code

def test_user_have_no_owner_permission(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    # in channels
    wrap_channel_join(False, user2_token, 1)
    assert wrap_message_pin(True, user2_token, 1) == AccessError.code
    wrap_message_pin(False, user1_token, 1)
    assert wrap_message_pin(True, user2_token, 1) == AccessError.code
    
    # in dms
    wrap_dm_create(False, user1_token, [2])
    wrap_message_senddm(False, user1_token, 3, "message id: 5")
    assert wrap_message_pin(True, user2_token, 5) == AccessError.code
    wrap_message_pin(False, user1_token, 5)
    assert wrap_message_pin(True, user2_token, 5) == AccessError.code
    
    