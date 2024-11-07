from tests.wrap_functions_test import *
from src.config import url
import requests
import pytest
from src.error import InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_proper_set_email(clear_data):
    need_status_code = False
    wrap_auth_register(need_status_code,'bb@163.com', '123weAre', 'Bob', 'Smi')
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    wrap_user_profile_set_email(True, authid['token'],'bob123@gmail.com')
    assert wrap_user_profile(need_status_code, authid['token'], 2) == {'user': {'user_id': 2, 'email': 'bob123@gmail.com', 'name_first': 'Jia', \
                'name_last': 'Cheng', 'handle_str': 'jiacheng', 'profile_img_url': url+'static/image.jpg'}}

#test if the email is in the right format
def test_invalid_email(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    assert wrap_user_profile_set_email(True, authid['token'],'bobgmail.com') == InputError.code
    assert wrap_user_profile_set_email(True, authid['token'],'eva@gmailcom') == InputError.code

#test if the email is repeated 
def test_email_being_used(clear_data):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"jiacheng@gmail.com", "223344", "Jia", "Cheng")
    wrap_auth_register(need_status_code,'bb@163.com', '123weAre', 'Bob', 'Smi')
    assert wrap_user_profile_set_email(True,authid['token'],'bb@163.com') == InputError.code
                               
