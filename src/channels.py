from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.config import url, SECRET
import jwt
from src.stats import user_stats_add_channel
from src.stats import stream_stats_add_channel

# check whether the token is valid
# if it is invalid, raise AccessError
# if it is valid, return the token's user id
def token_to_id(token):
    store = data_store.get()
    # check the format of the token
    session = {}
    try:
        session = jwt.decode(token, SECRET, algorithms=['HS256'])
    except Exception as exception:
        raise AccessError('Invalid token format, raised {exception}') from exception
    for user in store['users']:
        # if the user_id and session_id of the token is found
        # return the user_id to indicate a valid token
        if user['user_id'] == session['user_id'] and session['session_id'] in user['session_ids']:
            return user['user_id']
    raise AccessError('The session of the token is not valid')


# ------------------------------------- < channels_list > < channels_listall> ----------------------------------------
def channels_list(token):
    '''
    list all the channels the auth_user_id is part of
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains a list of dictionaries of channels that the auth_user_id is part of
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channel_list = []
    # loop through every channel
    for channel in store['channels']:
        # loop through every channel's member
        for user_id in channel['all_members']:
            if user_id == auth_user_id:
                channel_list.append({
                    'channel_id': channel['channel_id'],
                    'name': channel['channel_name'],
                })
                break
    return {
        'channels': channel_list
    }


def channels_listall(token):
    '''
    list all the channels ever been created
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
    
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains a list of dictionaries of all channels
    '''
    token_to_id(token)
    store = data_store.get()
    channel_list = []
    for channel in store['channels']:
        channel_list.append({
            'channel_id': channel['channel_id'],
            'name': channel['channel_name'],
        })
    return {
        'channels': channel_list
    }
    



# ------------------------------------- < channels_create > ----------------------------------------
# create a new channel dictionary (use for storing channel with its channel id)
def create_new_channel(auth_user_id, name, is_public):

    if len(name) > 20 or len(name) < 1 :
        raise InputError("Invalid channel name")
    
    return {
        'channel_name':name,
        'owner_members': [auth_user_id],
        'all_members':[auth_user_id],
        'messages':[],
        'standups':'',
        'is_public':is_public,
        'time_finish':None,
        'is_active':False 
    }


# crate a new channel using create_new_channel 
# give channels a channel id
def channels_create(token, name, is_public):
    '''
    create a new channel 
    
    Arguments:
        token(string) - an encoded string contains the user_id and session_id of an user
        name(string) - the name of the new channel created
        is_public(boolean) - the type of channel pravicy(private or public channel)

        
    Exceptions:
        InputError - Occurs when name is not valid(name less than 1 or more than 20 characters)
    
    Return Value:
        Returns a dictionary containing channel id
    '''
    data = data_store.get()
    '''
    if check_valid_user(data['token']) == False:
        raise AccessError("The id of the token doesn't exist")
    '''
    auth_user_id = token_to_id(token)
    channel_data = data['channels']
    channel_id = len(data['channels']) + 1

    new_channel = create_new_channel(auth_user_id, name, is_public)
    new_channel['channel_id'] = channel_id
    channel_data.append(new_channel)
    user_stats_add_channel(auth_user_id)
    stream_stats_add_channel()
    return {
        'channel_id': channel_id
    }

