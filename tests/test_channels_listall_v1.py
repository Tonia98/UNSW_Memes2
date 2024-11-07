import requests
from src.config import url
from src.error import AccessError
from tests.wrap_functions_test import *

# test the case if the token is not valid
def test_list_invalid():
    requests.delete(url + 'clear/v1')
    # test the case if the id of the token doesn't exist
    assert wrap_channels_listall(True, '1') == AccessError.code

# test the case if there is no channels in the stream
def test_listall_empty():
    requests.delete(url + 'clear/v1')
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert(wrap_channels_listall(False, user1['token']) == {
        'channels':[]
    })
# test all varieties of cases
def test_listall_valid():
    requests.delete(url + 'clear/v1')
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    channel1 = wrap_channels_create(False, user1['token'], "DODO", True)
    # if the token id doesn't exist
    assert wrap_channels_listall(True, '-1') == AccessError.code
    # only channel1 has ever been created
    assert(wrap_channels_listall(False, user1['token']) == {
        'channels': [
            {
                'channel_id': channel1['channel_id'],
                'name': 'DODO',
            },
        ]
    })
    # two channels been created
    channel2 = wrap_channels_create(False, user1['token'], "Plane", False)
    assert(wrap_channels_listall(False, user1['token']) == {
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
    })
    user2 = wrap_auth_register(False, "python@gmail.com", "python3", "python", "py")
    channel3 = wrap_channels_create(False, user2['token'], "Friends", True)
    # three channels been created
    assert(wrap_channels_listall(False, user1['token']) == {
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
                'name': 'Friends',
            },
        ]
    })
    # non exist token id
    wrap_channels_listall(True, '999') == AccessError.code
