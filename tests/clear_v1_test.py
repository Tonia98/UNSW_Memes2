import pytest
#from src.other import clear
from tests.wrap_functions_test import *
import requests
from src.config import url


# clearing with no input
def test_clearing_no_input():
    requests.delete(url + 'clear/v1')
    assert(wrap_clear() == {})


# clearing with only users in data_store
def test_cant_login_after_clear():
    requests.delete(url + 'clear/v1')
    wrap_clear()
    need_status_code = False
    wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    requests.delete(url + 'clear/v1')
    wrap_clear()
    need_status_code = True
    assert wrap_auth_login(need_status_code, "liy@gmail.com", "112233") == 400
    

# clearing with existing users and channels in data_store
def test_clearing_channel():
    requests.delete(url + 'clear/v1')
    wrap_clear()
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    channelid = wrap_channels_create(need_status_code, authid['token'], 'li', True)
    requests.delete(url + 'clear/v1')
    wrap_clear()
    need_status_code = True
    assert wrap_channel_join(need_status_code, authid['token'], channelid['channel_id']) == 403



