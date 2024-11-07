import pytest
import requests
from src.channel import *
from src.message import *
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
    assert wrap_user_remove(True, '1', user1['auth_user_id']) == AccessError.code
    
# test the case if the authorised user is not a global owner
def test_not_global(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user2 who is not a global owner trying to remove user1
    assert wrap_user_remove(True, user2['token'], user1['auth_user_id']) == AccessError.code
    
# test the case if uid is not valid
def test_invalid_uid(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    assert wrap_user_remove(True, user1['token'], 2) == InputError.code
    
# test the case the only global owner will be removed
def test_only_global(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_user_remove(True, user1['token'], user1['auth_user_id']) == InputError.code
    
# test if the ouput of the function is correct
def test_correct_output(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    assert wrap_user_remove(False, user1['token'], user2['auth_user_id']) == {}
    
# test if the user is removed successfully
def test_removed_successfully(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    # user2 cannot login
    assert wrap_auth_login(True, "wz37544@gmail.com", "37856904") == InputError.code
    # user2 cannot create a channel
    assert wrap_channels_create(True, user2['token'], "DODO", True) == AccessError.code
    channel1 = wrap_channels_create(False, user1['token'], "DODO", True)
    # user2 cannot be invited
    assert wrap_channel_invite(True, user1['token'], channel1['channel_id'], user2['auth_user_id']) == InputError.code
    
# test if users all cannot list the removed user
def test_removed_from_users(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    assert wrap_users_all(False, user1['token']) == {      
        'users': [
            {
                'u_id': user1['auth_user_id'],
                'email': "wayne@gmail.com",
                'name_first': "Wayne",
                'name_last': "Zhang",
                'handle_str': "waynezhang",
                'profile_img_url': url+'static/image.jpg',
            },
        ]
    }
    
# test if the user is removed from the channel the user is in
def test_removed_from_channel(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    user3 = wrap_auth_register(False, "uuu888@hotmail.com", "iamaman", "Raphael", "Wilson")
    # user1 created channel1
    channel1 = wrap_channels_create(False, user1['token'], "DODO", True)
    # user1 created channel2
    wrap_channels_create(False, user2['token'], "Snake", True)
    # user2 and user3 joined channel1
    wrap_channel_join(False, user2['token'], channel1['channel_id'])
    wrap_channel_join(False, user3['token'], channel1['channel_id'])
    wrap_channel_addowner(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    # user1 removed user2 and user3
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    wrap_user_remove(False, user1['token'], user3['auth_user_id'])
    # test if both owner and member are removed from channel1
    assert wrap_channel_details(False, user1['token'], channel1['channel_id']) == {
        'name': 'DODO',
        'is_public': True,
        'owner_members': [{
            'u_id': user1['auth_user_id'],
            'email': 'wayne@gmail.com',
            'name_first': 'Wayne',
            'name_last': 'Zhang',
            'handle_str': 'waynezhang',
            'profile_img_url': url+'static/image.jpg'
        }],
        'all_members': [{
            'u_id': user1['auth_user_id'],
            'email': 'wayne@gmail.com',
            'name_first': 'Wayne',
            'name_last': 'Zhang',
            'handle_str': 'waynezhang',
            'profile_img_url': url+'static/image.jpg'
        }],
    }

# test if the user is removed from the dm the user is in
def test_removed_from_dm(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    user3 = wrap_auth_register(False, "uuu888@hotmail.com", "iamaman", "Raphael", "Wilson")
    # user2 created dm1 includes user1 and user3
    dm1 = wrap_dm_create(False, user2['token'], [user1['auth_user_id'], user3['auth_user_id']])
    wrap_dm_create(False, user1['token'], [user2['auth_user_id']])
    # user1 removed user2 and user3
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    wrap_user_remove(False, user1['token'], user3['auth_user_id'])
    # test if both owner and member are removed from dm1
    assert wrap_dm_details(False, user1['token'], dm1['dm_id']) == {
        'name': 'jasonleo, raphaelwilson, waynezhang',
        'members': [
            {
                'u_id': user1['auth_user_id'],
                'email': 'wayne@gmail.com',
                'name_first': 'Wayne',
                'name_last': 'Zhang',
                'handle_str': 'waynezhang',
                'profile_img_url': url+'static/image.jpg'
            }
        ]
    }
    
# test if the removed user's profile's name is changed to 'Removed' and 'user'
def test_profile_with_correct_name(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    assert wrap_user_profile(False, user1['token'], user2['auth_user_id']) == {
        'user':{
            'user_id': 2, 
            'email': 'wz37544@gmail.com', 
            'name_first': 'Removed', 
            'name_last': 'user', 
            'handle_str': 'jasonleo',
            'profile_img_url': url+'static/image.jpg'
        }
    }
    
# test if the channel message becomes 'Removed user'
def test_correct_channel_message_after_removed(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user1 created channel1
    channel1 = wrap_channels_create(False, user1['token'], "DODO", True)
    # user2 joined channel1
    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    # user2 says 'hello'
    wrap_message_send(False, user2['token'], channel1['channel_id'], 'hello')
    wrap_message_send(False, user1['token'], channel1['channel_id'], 'I am going to remove you')
    # user1 removed user2
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    # test if the message becomes 'Removed user'
    message = wrap_channel_messages(False, user1['token'], channel1['channel_id'], 0)
    assert message['messages'][1]['message'] == 'Removed user'

# test if the dm message becomes 'Removed user'
def test_correct_dm_message_after_removed(setup):
    user1 = wrap_auth_register(False, "wayne@gmail.com", "123456", "Wayne", "Zhang")
    user2 = wrap_auth_register(False, "wz37544@gmail.com", "37856904", "Jason", "Leo")
    # user1 created dm1 includes user2
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])
    # user2 says 'hello'
    wrap_message_senddm(False, user2['token'], dm1['dm_id'], 'hello')
    wrap_message_senddm(False, user1['token'], dm1['dm_id'], 'I am going to remove you')
    # user1 removed user2
    wrap_user_remove(False, user1['token'], user2['auth_user_id'])
    # test if the message becomes 'Removed user'
    message = wrap_dm_messages(False, user1['token'], dm1['dm_id'], 0)
    assert message['messages'][1]['message'] == 'Removed user'

    
    
    

