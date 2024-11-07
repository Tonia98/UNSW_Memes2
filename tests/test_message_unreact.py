import pytest
import requests
from src.config import url
from tests.wrap_functions_test import *
from src.error import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

def test_invalid_react_id(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid =wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    need_status_code = True
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 0) == InputError.code

def test_invalid_unreacting_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    messageid =wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    need_status_code = True
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code

def test_invalid_unreacting_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    need_status_code = True
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code


def test_message_id_invalid_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    channelid1 = wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    messageid = wrap_message_send(need_status_code, authid1['token'], channelid1['channel_id'], 'sample message')
    need_status_code = True
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code
    

def test_message_id_invalid_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "668843499", "yi", "lee")
    authid3 = wrap_auth_register(need_status_code, "thisissampel@gmail.com", "09887633", "josh", "cho")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    dmid1 = wrap_dm_create(need_status_code, authid2['token'], [authid3['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    messageid = wrap_message_senddm(need_status_code, authid2['token'], dmid1['dm_id'], 'sample message')
    need_status_code = True
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == InputError.code
    

def test_success_unreact_channel(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    wrap_channels_create(need_status_code, authid1['token'], 'ling', True)
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'sample')
    wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'more messages')
    messageid = wrap_message_send(need_status_code, authid['token'], channelid['channel_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    # test if user has successfully unreacted to message in channel
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == {}

def test_success_unreact_dm(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dmid = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid1['token'], dmid['dm_id'], 'sample')
    wrap_message_senddm(need_status_code, authid1['token'], dmid['dm_id'], 'another message')
    messageid = wrap_message_senddm(need_status_code, authid['token'], dmid['dm_id'], 'something')
    wrap_message_react(need_status_code, authid['token'], messageid['message_id'], 1)
    # test if user has successfully unreacted to message in DM
    assert wrap_message_unreact(need_status_code, authid['token'], messageid['message_id'], 1) == {}
