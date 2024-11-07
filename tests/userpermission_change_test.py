import pytest
import requests
from src.config import url
from src.error import AccessError
from src.error import InputError
from tests.wrap_functions_test import *

global_owner = 1
global_member = 2

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

# test the case if the token is not valid
def test_invalid_token(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_userpermission_change(True, '1', user1['auth_user_id'], global_owner) == AccessError.code
    
# test the case if the auth is not a global owner
def test_not_global(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_userpermission_change(True, user2['token'], user1['auth_user_id'], global_owner) == AccessError.code

# test the case if the u_id is the only global owner
def test_only_global(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_userpermission_change(True, user1['token'], user1['auth_user_id'], global_member) == InputError.code

# test the case if the u_id is not valid
def test_invalid_uid(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_userpermission_change(True, user1['token'], 3, global_member) == InputError.code
    
# test the case if the permission id is not valid
def test_invalid_permission_id(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_userpermission_change(True, user1['token'], user2['auth_user_id'], 3) == InputError.code

# test if the output of the function is correct 
def test_output(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_userpermission_change(False, user1['token'], user2['auth_user_id'], global_owner) == {}   

# test the if someone can be set to global owner successfully
def test_set_to_owner(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user1 created a private channel
    channel1 = wrap_channels_create(False, user1['token'], "DODO", False)
    # user2 is set to be global owner by user1
    wrap_userpermission_change(False, user1['token'], user2['auth_user_id'], global_owner)
    # check if user2 can join the private channel
    assert wrap_channel_join(True, user2['token'], channel1['channel_id']) == 200
    
# test if someone can be set to global member successfully
def test_set_to_member(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user2 created a private channel
    channel1 = wrap_channels_create(False, user2['token'], "DODO", False)
    # user2 is promoted to a global owner by user1
    wrap_userpermission_change(False, user1['token'], user2['auth_user_id'], global_owner)
    # user1 is demoted to a global member by user2
    wrap_userpermission_change(False, user2['token'], user1['auth_user_id'], global_member)
    # make sure user1 can't join the private channel
    assert wrap_channel_join(True, user1['token'], channel1['channel_id']) == AccessError.code



