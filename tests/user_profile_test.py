from src.channels import token_to_id
from tests.wrap_functions_test import *
from src.admin import *
import requests
from src.config import url
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

# list information of profile of a valid user
def test_proper_profile(clear_data):
    token_id1 = wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    wrap_auth_register(False,'ok@163.com', '123weAre', 'Bob', 'Smi')
    user = wrap_user_profile(False, token_id1['token'], 2)
    assert user == {'user': {'user_id': 2, 'email': 'ok@163.com', 'name_first': 'Bob', \
                                        'name_last': 'Smi', 'handle_str': 'bobsmi0', 'profile_img_url': url+'static/image.jpg'}}

# provided u_id can not be found 
def test_uid_not_valid(clear_data):
    token_id1 = wrap_auth_register(False,'kk@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile(True, token_id1['token'], 2) == InputError.code
    wrap_auth_register(False,'ss@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile(True, token_id1['token'], 3) == InputError.code

# list the removed user's profile
def test_user_is_removed(clear_data):
    token_id1 = wrap_auth_register(False,'kk@163.com', '123weAre', 'Bob', 'Smi')
    wrap_auth_register(False,'bb@163.com', '123weAre', 'Bob', 'Smi')
    wrap_user_remove(False, token_id1['token'], 2)
    wrap_user_profile(False, token_id1['token'], 2) == {'user': {'user_id': 2, 
                                                        'email': 'bb@163.com', 
                                                        'name_first': 'Removed', 
                                                        'name_last': 'user', 
                                                        'handle_str': 'bobsmi0',
                                                        'profile_img_url': url+'static/image.jpg'
                                                        }}
    # register one more user and remove it and check if it is removed                                                   
    wrap_auth_register(False,'b@163.com', '123weAre', 'Bob', 'Smi')
    wrap_user_remove(False, token_id1['token'], 3)
    wrap_user_profile(False, token_id1['token'], 3) == {'user': {'user_id': 3, 
                                                        'email': 'b@163.com', 
                                                        'name_first': 'Removed', 
                                                        'name_last': 'user', 
                                                        'handle_str': 'bobsmi1',
                                                        'profile_img_url': url+'static/image.jpg'
                                                        }}
