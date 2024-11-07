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
    assert wrap_channels_list(True, '1') == AccessError.code
    
        
# test the case if there is no channels in the stream
def test_list_empty(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_channels_list(False, user1['token']) == {
        'channels':[]
    }


def test_list_valid(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # non exist token id
    assert wrap_channels_list(True, '-1') == AccessError.code
    # user1 created channel1
    channel1 = wrap_channels_create(False, user1['token'], "DODO", True)
    # user1 is only part of channel1
    assert wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'DODO',
            },
        ]
    }
    # user1 created channel2
    channel2 = wrap_channels_create(False, user1['token'], "Plane", False)
    # user2 is not in any channels
    assert wrap_channels_list(False, user2['token']) == {
        'channels':[]
    }
    # user2 created channel3
    channel3 = wrap_channels_create(False, user2['token'], "Motor", False)
    # user1 takes part in channel1 and channel2
    assert wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'DODO',
            },
            {
                'channel_id': channel2['channel_id'],
                'name': 'Plane',
            },
        ]
    }
    # user2 takes part in channel3
    assert wrap_channels_list(False, user2['token']) == {
        'channels': [
            {
                'channel_id': channel3['channel_id'],
                'name': 'Motor',
            },
        ]
    }
    # user1 invites user2 to channel1
    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    # user2 takes part in channel1 and channel3
    assert(wrap_channels_list(False, user2['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'DODO',
            },
            {
                'channel_id': channel3['channel_id'],
                'name': 'Motor',
            },
        ]
    })
    # user2 invites user1 to channel3
    wrap_channel_invite(False, user2['token'], channel3['channel_id'], user1['auth_user_id'])
    # user1 takes part in all 3 channels
    assert(wrap_channels_list(False, user1['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'DODO',
            },
            {
                'channel_id': channel2['channel_id'],
                'name': 'Plane',
            },
            {
                'channel_id': channel3['channel_id'],
                'name': 'Motor',
            },
        ]
    })
