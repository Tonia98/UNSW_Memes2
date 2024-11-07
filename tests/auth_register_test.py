import requests
from src.config import url
from src.auth import generate_token
from tests.wrap_functions_test import *
import pytest
from src.error import AccessError, InputError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

'''
this test function should be pass, cause given parameters 
are all correct.
'''
def test_valid_register(clear_data):
    assert wrap_auth_register(False, 'bob@gmail.com', '123weAreFriends', \
            'Bob', 'Smith') == {'token': generate_token(1, 1), 'auth_user_id': 1}
    assert wrap_auth_register(False, 'Amy@gmail.com', '123weAreFriends', \
            'Amy', 'Smith') == {'token': generate_token(2, 2), 'auth_user_id': 2}
    assert wrap_auth_register(False, 'eva@gmail.com', '123weAreFriends', \
            'Eva', 'Smith') == {'token': generate_token(3, 3), 'auth_user_id': 3}
    

'''
This test function should raise an input error.
Email is invalid (wrong email address form).
'''
def test_invalid_email(clear_data):
    assert wrap_auth_register(True, 'bobgmail.com', '123weAreFriends',\
                                'Bob', 'Smith') == InputError.code
    assert wrap_auth_register(True, 'eva@gmailcom', '123weAreFriends',\
                                'Eva', 'Smith') == InputError.code

 
'''
This test function should raise an input error.
Because email address has been used by another user
'''
def test_email_being_used(clear_data):
    wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends', 'Bob', 'Smith')
    wrap_auth_register(True, 'eva@gmail.com', '123weAreFriends', 'Eva', 'Smith')
    assert wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends',\
                                 'Eva', 'Smith') == InputError.code

'''
This test function should raise an input error.
Because length of password is less than 6 characters
'''
def test_password_length_less_than_6(clear_data):
    assert wrap_auth_register(True, 'bob@gmail.com','123', 'Eva', 'Smith') == InputError.code
    assert wrap_auth_register(True, 'bob@gmail.com', 'wqe21', 'Eva', 'Smith') == InputError.code
    assert wrap_auth_register(True, 'bob@gmail.com', 'rew', 'Eva', 'Smith') == InputError.code
                                
        
''''
This test function should raise an input error.
Because length of first name or last name is not between 1 and 50 characters inclusive
'''
def test_invalid_name(clear_data):
    assert wrap_auth_register(True, 'bob@gmail.com', \
                                '123weAreFriends', '', 'Smith') == InputError.code

    assert wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends', 
    'Evahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh','Smith') == InputError.code 

    assert wrap_auth_register(True, 'bob@gmail.com', \
                                        '123weAreFriends', 'Eva', '') == InputError.code

    assert wrap_auth_register(True, 'bob@gmail.com', '123weAreFriends', 'Smith',
    'Evahhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh') == InputError.code 

def new_account_handle(email, password, name_first, name_last):
    user_id = wrap_auth_register(False, email, password, name_first, name_last)
    channel_id = wrap_channels_create(False, user_id['token'], "DODO", True)
    channel_details = wrap_channel_details(False, user_id['token'], channel_id['channel_id'])
    handle = channel_details['all_members'][0]['handle_str']
    return handle

# check if the generated handle is lowercase-only
def test_handle_lowercase_only(clear_data):
    handle = new_account_handle('Bob@gmail.com', '123weAreFriends', "Bob", 'Smith')
    assert handle == "bobsmith"

# check whether a number will be append in the end of handle, if two user have the same name.
def test_handle_same_handle():
    handle = new_account_handle('Bb@gmail.com', '123weAreFriends', "Bob", 'Smith')
    assert handle == "bobsmith0"
    handle2 = new_account_handle('Bowb@gmail.com', '123weAreFriends', "Bob", 'Smith')
    assert handle2 == "bobsmith1"

# check if the lenth of handle will be 20, if raw lenth of handle exceed 20
def test_handle_exceed_20(clear_data):
    handle = new_account_handle('Bas@gmail.com', '123weAreFriends', "SuhaolanDorisDaiSusan", 'Smith')
    assert handle == "suhaolandorisdaisusa"

# check if handle is appended a correct number when handle exceed 20 and two users have the same raw handle
def test_handle_same_handle_exceed_20():

    handle = new_account_handle('lob@gmail.com', '123weAreFriends', "SuhaolanDorisDaiSusan", 'Smith')
    assert handle == "suhaolandorisdaisusa0"
    handle2 = new_account_handle('Baaab@gmail.com', '123weAreFriends', "SuhaolanDorisDaiSusan", 'Smith')
    assert handle2 == "suhaolandorisdaisusa1"
