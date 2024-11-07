import pytest
import requests
from src.config import url
from src.error import AccessError
from tests.wrap_functions_test import *

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')


# test the case if the token is not valid
def test_list_invalid(setup):
    # test the case if the id of the token doesn't exist
    assert wrap_dm_list(True, '1') == AccessError.code
    
        
# test the case if there is no dm in the stream
def test_list_empty(setup):
    need_status_code = False 
    user1 = wrap_auth_register(need_status_code, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_dm_list(need_status_code, user1['token']) == {
        'dms':[]
    }


def test_proper_list_single(setup):
    need_status_code = False 
    user1 = wrap_auth_register(need_status_code, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(need_status_code, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # non exist token id
    assert wrap_dm_list(True, '-1') == AccessError.code
    # user1 created dm1
    dm1 = wrap_dm_create(need_status_code, user1['token'], [])
    # user1 is only part of dm1
    assert wrap_dm_list(need_status_code, user1['token']) == {
        'dms': [
            {
                'dm_id': dm1['dm_id'],
                'name': 'waynezhang',
            },
        ]
    }
    # user1 also created dm2
    dm2 = wrap_dm_create(need_status_code, user1['token'], [])
    # user2 is not in any dms
    assert wrap_dm_list(need_status_code, user2['token']) == {
        'dms':[]
    }
    # user2 created dm3
    dm3 = wrap_dm_create(need_status_code, user2['token'], [])

    # user1 takes part in dm1 and dm2
    assert wrap_dm_list(need_status_code, user1['token']) == {
        'dms': [
            {
                'dm_id': dm1['dm_id'],
                'name': 'waynezhang',
            },
            {
                'dm_id': dm2['dm_id'],
                'name': 'waynezhang',
            },
        ]
    }
    # user2 takes part in dm3
    assert wrap_dm_list(False, user2['token']) == {
        'dms': [
            {
                'dm_id': dm3['dm_id'],
                'name': 'jasonleo',
            },
        ]
    }

def test_proper_list_multiple(setup):
    need_status_code = False 
    user1 = wrap_auth_register(need_status_code, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(need_status_code, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    dm = wrap_dm_create(need_status_code, user1['token'], [user2['auth_user_id']])
    assert wrap_dm_list(need_status_code, user1['token']) == {
    'dms': [
        {
            'dm_id': dm['dm_id'],
            'name': 'jasonleo, waynezhang'
        }
    ]
}