import pytest
import requests
from tests.wrap_functions_test import *
from src.config import url
from src.error import AccessError

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
# test the case if the token is not valid
def test_invalid(setup):
    assert wrap_users_all(True, '1') == AccessError.code
    
# test the case if there is only one user
def test_one(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_users_all(False, user1['token']) == {
        'users': [
            {
                'u_id': user1['auth_user_id'],
                'email': "wayne@gmail.com",
                'name_first': "Wayne",
                'name_last': "Zhang",
                'handle_str': "waynezhang", 
                'profile_img_url': url+'static/image.jpg'
            }
        ]
    }

# test the case if there are two users
def test_two(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_users_all(False, user1['token']) == {
        'users': [
            {
                'u_id': user1['auth_user_id'],
                'email': "wayne@gmail.com",
                'name_first': "Wayne",
                'name_last': "Zhang",
                'handle_str': "waynezhang",
                'profile_img_url': url+'static/image.jpg'
            },
            {
                'u_id': user2['auth_user_id'],
                'email': "wz37544@gmail.com",
                'name_first': "Jason",
                'name_last': "Leo",
                'handle_str': "jasonleo",
                'profile_img_url': url+'static/image.jpg'
            }
        ]
    }
  
# a test just to clear database  
def test_clear(setup):
    pass
    
