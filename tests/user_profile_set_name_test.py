from tests.wrap_functions_test import *
from src.channels import token_to_id
import requests
from src.config import url
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# give valid first name and last name, change auth_user's first name and last name to new name
def test_proper_set_name(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    token_id2 = wrap_auth_register(False,'b@163.com', '123weAre', 'Bob', 'Smi')
    
    wrap_user_profile_set_name(False, token_id1['token'], 'BokB', 'Smit')
    profile = {'user': {'user_id': 1, 'email': 'bb@163.com', 'name_first': 'BokB', \
                'name_last': 'Smit', 'handle_str': 'bobsmi', 'profile_img_url': url+'static/image.jpg'}}
    assert wrap_user_profile(False, token_id1['token'], 1) == profile

    wrap_user_profile_set_name(False, token_id2['token'], 'BB', 'St')
    profile = {'user': {'user_id': 2, 'email': 'b@163.com', 'name_first': 'BB', \
                'name_last': 'St', 'handle_str': 'bobsmi0', 'profile_img_url': url+'static/image.jpg'}}
    assert wrap_user_profile(False, token_id1['token'], 2) == profile

# given length of first name is greater than 50 or empty
def test_len_name_first_is_not_proper(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile_set_name(True, token_id1['token'], 'Evahhhhhhhhhhh\
    hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', 'Smit') == InputError.code 

    assert wrap_user_profile_set_name(True, token_id1['token'], '', 'Smit') == InputError.code 

    assert wrap_user_profile_set_name(True, token_id1['token'], '', '') == InputError.code 

# given length of first name is greater than 50 or empty
def test_len_name_last_is_not_proper(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')

    assert wrap_user_profile_set_name(True, token_id1['token'], 'Smit', 'Evahhhhhhhhhhh\
    hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh') == InputError.code 

    assert wrap_user_profile_set_name(True, token_id1['token'], 'dfjdk', '') == InputError.code 

    
    
