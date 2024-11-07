import requests
from src.config import url
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError
from tests.message_pin_test import basic_function_set_up, get_channel_or_dm_message

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_unpin_messsage_successfully(clear_data):
    (user1_token, user2_token) = basic_function_set_up()

    wrap_channel_join(False, user1_token, 2)
    wrap_message_pin(True, user1_token, 1)
    wrap_message_pin(True, user1_token, 2)
    wrap_message_pin(True, user1_token, 3)
    wrap_message_pin(True, user2_token, 4)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    # test if message is pinned
    assert channel2_m['messages'][0]['is_pinned'] == True
    assert dm1_m['messages'][0]['is_pinned'] == True
    assert dm2_m['messages'][0]['is_pinned'] == True

    wrap_message_unpin(True, user1_token, 2)
    wrap_message_unpin(True, user1_token, 1)
    wrap_message_unpin(True, user1_token, 3)
    wrap_message_unpin(True, user2_token, 4)
    (channel1_m, channel2_m, dm1_m, dm2_m) = get_channel_or_dm_message(user1_token, user2_token)
    # test if message has successfully unpinned
    assert channel2_m['messages'][0]['is_pinned'] == False
    assert channel1_m['messages'][0]['is_pinned'] == False
    assert dm1_m['messages'][0]['is_pinned'] == False
    assert dm2_m['messages'][0]['is_pinned'] == False

def test_unpin_invalid_message_id(clear_data):
    (user1_token, user2_token) = basic_function_set_up()

    wrap_message_pin(True, user1_token, 1)
    assert wrap_message_unpin(True, user2_token, 1) == InputError.code
    assert wrap_message_unpin(True, user2_token, 5) == InputError.code
    
    # in dms
    wrap_message_pin(True, user2_token, 4)
    wrap_message_pin(True, user1_token, 3)
    assert wrap_message_unpin(True, user1_token, 4) == InputError.code
    assert wrap_message_unpin(True, user2_token, 3) == InputError.code
    
def test_message_is_already_not_pinned(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    assert wrap_message_unpin(True, user1_token, 1) == InputError.code
    assert wrap_message_unpin(True, user1_token, 2) == InputError.code
    wrap_message_pin(True, user1_token, 1)
    wrap_message_pin(True, user1_token, 2)
    wrap_message_unpin(True, user1_token, 1)
    wrap_message_unpin(True, user1_token, 2)
    assert wrap_message_unpin(True, user1_token, 1) == InputError.code
    assert wrap_message_unpin(True, user1_token, 2) == InputError.code
    
    # in dms
    assert wrap_message_unpin(True, user1_token, 3) == InputError.code
    assert wrap_message_unpin(True, user2_token, 4) == InputError.code
    wrap_message_pin(True, user2_token, 4)
    wrap_message_pin(True, user1_token, 3)
    wrap_message_unpin(True, user1_token, 3)
    wrap_message_unpin(True, user2_token, 4)
    assert wrap_message_unpin(True, user1_token, 3) == InputError.code
    assert wrap_message_unpin(True, user2_token, 4) == InputError.code
    
def test_user_does_not_have_owner_permission_to_unpin(clear_data):
    (user1_token, user2_token) = basic_function_set_up()
    wrap_channel_join(False, user2_token, 1)
    assert wrap_message_unpin(True, user2_token, 1) == AccessError.code
    wrap_message_pin(True, user1_token, 1)
    assert wrap_message_unpin(True, user2_token, 1) == AccessError.code
    
    # in dms
    wrap_dm_create(False, user2_token, [1])
    wrap_message_senddm(False, user2_token, 3, "message id: 5")
    assert wrap_message_unpin(True, user1_token, 5) == AccessError.code
    wrap_message_pin(True, user2_token, 4)
    assert wrap_message_unpin(True, user1_token, 5) == AccessError.code
    
