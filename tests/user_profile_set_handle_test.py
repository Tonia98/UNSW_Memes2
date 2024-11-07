from src.channels import token_to_id
from tests.wrap_functions_test import *
import requests
from src.config import url
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# give a valid new handle string, change auth_user's handle to new handle
def test_proper_set_handle(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    token_id2 = wrap_auth_register(False,'b@163.com', '123weAre', 'Bob', 'Smi')
    
    wrap_user_profile_set_handle(True, token_id1['token'], 'youyou0')
    arguments = {'user': {'user_id': 1, 'email': 'bb@163.com', 'name_first': 'Bob', \
                'name_last': 'Smi', 'handle_str': 'youyou0', 'profile_img_url': url+'static/image.jpg'}}
    assert wrap_user_profile(False, token_id1['token'], 1) == arguments

    wrap_user_profile_set_handle(True, token_id2['token'], 'YAH0')
    arguments = {'user': {'user_id': 2, 'email': 'b@163.com', 'name_first': 'Bob', \
                'name_last': 'Smi', 'handle_str': 'YAH0', 'profile_img_url': url+'static/image.jpg'}}
    assert wrap_user_profile(False, token_id1['token'], 2) == arguments

# length of given handle string is not between 3 to 20
def test_len_handle_str_not_proper(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile_set_handle(True, token_id1['token'], '') == InputError.code 
    assert wrap_user_profile_set_handle(True, token_id1['token'], 'a') == InputError.code 
    assert wrap_user_profile_set_handle(True, token_id1['token'], 'ab') == InputError.code 
    assert wrap_user_profile_set_handle(True, token_id1['token'], 'hhhhhhhhhhh\
                                        hhhhhhhhhhhhhhh') == InputError.code 

# length of given handle string is not alpha numeric
def test_hendle_str_are_not_alphanumeric(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile_set_handle(True, token_id1['token'], 'youyou_0') == InputError.code 
    assert wrap_user_profile_set_handle(True, token_id1['token'], '[]***]') == InputError.code 

# given handle string is already used by another user
def test_handle_is_already_used(clear_data):
    wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    token_id2 = wrap_auth_register(False,'ok@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile_set_handle(True, token_id2['token'], 'bobsmi') == InputError.code 
    assert wrap_user_profile_set_handle(True, token_id2['token'], 'bobsmi0') == InputError.code 
    
