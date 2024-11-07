import requests
from src.config import url
import pytest
from src.error import InputError
from tests.wrap_functions_test import *

# test for the channels_create_v1 function output channel_id
@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

def test_valid_create_id(setup):
    need_status_code = False 
    tokenid = wrap_auth_register(need_status_code, 'bob@gmail.com', \
            '123weAreFriends', 'Bob', 'Smith') # {'token': '1', 'auth_user_id': 1}
    assert wrap_channels_create(need_status_code, tokenid['token'], \
            'Snake',True) == {'channel_id': 1}
    assert wrap_channels_create(need_status_code, tokenid['token'], \
            'Tetris',False) == {'channel_id': 2}
   

# test name length less than 1 characters 
# raise InputError
def test_create_short(setup):
    need_status_code = False
    tokenid = wrap_auth_register(need_status_code, 'bob@gmail.com', \
            '123weAreFriends', 'Bob', 'Smith') # {'token': '1', 'auth_user_id': 1}
    assert wrap_channels_create(True,tokenid['token'],'',True) == InputError.code
         
# test name length more than 20 characters 
# raise InputError
def test_create_long(setup):
    need_status_code = False 
    tokenid = wrap_auth_register(need_status_code, 'bob@gmail.com', \
            '123weAreFriends', 'Bob', 'Smith') # {'token': '1', 'auth_user_id': 1}
    assert wrap_channels_create(True,tokenid['token'],'Abcdefghijklmnopqrestuvwsyz',True) == InputError.code
   
    
    
