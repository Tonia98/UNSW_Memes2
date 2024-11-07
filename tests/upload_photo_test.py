import pytest
import requests
from tests.wrap_functions_test import *
from src.config import url
from src.error import AccessError
from src.error import InputError
from src.config import url
from PIL import Image

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
def test_invalid_token(setup):
    assert wrap_uploadphoto(True, 'nottoken', 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 0, 0, 10, 10) == AccessError.code
    
def test_invalid_url(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_uploadphoto(True, user1['token'], 'noturl', 0, 0, 10, 10) == InputError.code
    
def test_end_less_than_start(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    # if x_end is less than x_start
    assert wrap_uploadphoto(True, user1['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 10, 5, 5, 10) == InputError.code
    # if y_end is less than y_start
    assert wrap_uploadphoto(True, user1['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 5, 10, 10, 5) == InputError.code
    
def test_not_within_dimension(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    # try to crop the image with very large cropping numbers
    wrap_uploadphoto(False, user1['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 10000, 10000, 20000, 20000)
    
def test_not_jpg(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    # upload a png photo, it should fail
    assert wrap_uploadphoto(True, user1['token'], 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png', 0, 0, 10, 10) == InputError.code
    
def test_uploaded(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user1 uploads a photo
    wrap_uploadphoto(False, user1['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 0, 0, 100, 100)
    # user2 uploads a photo
    wrap_uploadphoto(False, user2['token'], 'http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg', 0, 0, 200, 200)
    profile1 = wrap_user_profile(False, user1['token'], user1['auth_user_id'])
    auth_user_id = user1['auth_user_id']
    # user1 should get the right server url
    assert profile1['user']['profile_img_url'] == url + f'static/image{auth_user_id}.jpg'
    profile2 = wrap_user_profile(False, user2['token'], user2['auth_user_id'])
    auth_user_id = user2['auth_user_id']
    # user2 should get the right server url
    assert profile2['user']['profile_img_url'] == url + f'static/image{auth_user_id}.jpg'
    
# a test only clears the static folder to make it more convenient
def test_nothing(setup):
    pass
    
    
