import pytest
import requests
from src.config import url
from src.error import AccessError
from src.error import InputError
from tests.wrap_functions_test import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
# test the case if the token is not valid
def test_invalid_token(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_dm_create(True, '1', [user1['auth_user_id']]) == AccessError.code
    
# test the case if the uids is not valid
def test_invalid_uids(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_dm_create(True, user1['token'], [3]) == InputError.code
    assert wrap_dm_create(True, user1['token'], [user2['auth_user_id'], 3]) == InputError.code
    
# test the case if u_id is empty
def test_empty_uids(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_dm_create(False, user1['token'], []) == {'dm_id': 1}

# test if dm_ids are generated correctly
def test_correct_dm_ids(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    user3 = wrap_auth_register(False, "lol@hotmail.com", "456789", "Raphael", "Wilson")
    # user1 created a dm
    # make sure it has an id 1
    assert wrap_dm_create(False, user1['token'], [user2['auth_user_id']]) == {'dm_id': 1}
    # user1 created a same dm
    # make sure it has an id 2
    assert wrap_dm_create(False, user1['token'], [user2['auth_user_id']]) == {'dm_id': 2}
    # user1 created a different dm
    # make sure it has an id 3
    assert wrap_dm_create(False, user1['token'], [user2['auth_user_id'], user3['auth_user_id']]) == {'dm_id': 3}
    
    
    
