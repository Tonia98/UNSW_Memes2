import pytest, requests, math
from src.config import url
from tests.wrap_functions_test import *
from src.error import *
from datetime import datetime, timezone
@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

# when start is greater than 0 and no messages are sent
def test_start_greater_than_messages(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    need_status_code = True
    assert wrap_dm_messages(need_status_code, authid['token'], 1, 50) == InputError.code


# test dm_id does not refer to a valid dm
def test_dm_id_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    # input a random dm_id that is not valid with valid user_id
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    wrap_dm_create(need_status_code, authid['token'], authid1['token'])
    need_status_code = True 
    assert wrap_dm_messages(need_status_code, authid['token'],5, 0) == InputError.code
    assert wrap_dm_messages(need_status_code, authid['token'],9, 0) == InputError.code

# test valid dm_id with invalid user
def test_dm_id_valid_user_invalid(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code, "liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    authid2 = wrap_auth_register(need_status_code, "sample@gmail.com", "559988", "lyn", "jiang")
    wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    need_status_code = True
    # input the incorrect user_id with a valid dm_id that the user is not belong to
    assert wrap_dm_messages(need_status_code, authid2['token'], 1, 0) == AccessError.code

# test all inputs are correct as required
def test_empty_success(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    # this input will return a empty list for messages as no messages are in data_store
    assert wrap_dm_messages(need_status_code, authid1['token'], dm['dm_id'], 0) == {
        'messages': [],
        'start': 0,
        'end': -1,
    }

# testing only one message is send in dm
def test_single_success(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'This is a direct message from the owner')
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_dm_messages(need_status_code, authid1['token'], dm['dm_id'], 0) == {
        'messages': [{
            'message_id': 1,
            'u_id': 1,
            'message': 'This is a direct message from the owner',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1,
    }

# testing multiple messages are sent in dm
def test_multiple_success(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'This is a direct message from the owner')
    wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'Juice')
    wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'Hello World')
    # this input will return a empty list for messages as no messages are in data_store
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    assert wrap_dm_messages(need_status_code, authid1['token'], dm['dm_id'], 0) == {
        'messages': [{
            'message_id': 3,
            'u_id': 1,
            'message': 'Hello World',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        },
        {
            'message_id': 2,
            'u_id': 1,
            'message': 'Juice',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'This is a direct message from the owner',
            'time_created': pytest.approx(timestamp, abs=2),
            'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
            }],
            'is_pinned': False
        }],
        'start': 0,
        'end': -1,
    }

# test when there are over 50 message existing in dm data_store
def test_over_50_message_existing(setup):
    need_status_code = False
    authid = wrap_auth_register(need_status_code,"liy@gmail.com", "112233", "li", "yu")
    authid1 = wrap_auth_register(need_status_code, "true@gmail.com", "557788", "ling", "lin")
    dm = wrap_dm_create(need_status_code, authid['token'], [authid1['auth_user_id']])
    i = 0
    '''
    in this case, it is only testing for the start and end return value 
    as timestamp may vary due to how fast the system runs all tests
    '''
    
    while i < 50:
        wrap_message_senddm(need_status_code, authid['token'], dm['dm_id'], 'Hello World')
        i += 1
    result = wrap_dm_messages(need_status_code, authid['token'], dm['dm_id'], 0)
    assert result['start'] == 0
    assert result['end'] == 50
