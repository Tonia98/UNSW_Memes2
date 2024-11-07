from src.config import *
from src.error import *
import jwt
from src.data_store import data_store
import requests, string, re
from src.config import url
from src.channels import token_to_id


def notifications_get(token):
    '''
    send at most 20 notifications for a user
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns the user's most recent 20 notifcations, ordered from most recent to least recent
    '''
    

    auth_user_id = token_to_id(token)
    store = data_store.get()
    
    notification_message = []
    # valid u_id
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            notification_message = user['notifications'][-20 :]
    
    return {
        "notifications": notification_message
    }


# get the name of either channel or dm
def get_name(channel_id, dm_id):
    store = data_store.get()
    if channel_id == -1:
        for dm in store['dms']:
            if dm['dm_id'] == dm_id:
                return dm['dm_name']
    else: 
        for channel in store['channels']:
            if channel['channel_id'] == channel_id:
                return channel['channel_name']

# check if the handle belongs to a user
def valid_handle(handle):
    store = data_store.get()
    for user in store['users']:
        if user['handle'] == handle:
            return True
    return False

# convert a handle to user id
def handle_to_id(handle):
    store = data_store.get()
    for user in store['users']:
        if user['handle'] == handle:
            return user['user_id']

# given a user id, get the user's handle
def get_handle(u_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == u_id:
            return user['handle']

# check if the user is in either channel or dm
def user_in_channel_dm(user_id, channel_id, dm_id):
    store = data_store.get()
    if channel_id == -1:
        for dm in store['dms']:
            if dm['dm_id'] == dm_id:
                if user_id in dm['members']:
                    return True
                else:
                    return False
    else:
        for channel in store['channels']:
            if channel['channel_id'] == channel_id:
                if user_id in channel['all_members']:
                    return True
                else:
                    return False
                    
# tag a user in based on the message if eligible and add notification
def notification_tag(auth_user_id, channel_id, dm_id, message):
    store = data_store.get()
    
    # get all alphnumeric characters in a string
    alphanum = string.ascii_lowercase + string.ascii_uppercase + string.digits
    nonalphanum = string.printable
    # delete all alphanumeric characters from all characters to get the nonalphanumeric characters
    for c in string.printable:
        if c in alphanum:
            nonalphanum = nonalphanum.replace(c, '')
    regular_exp = '|'.join(map(re.escape, nonalphanum))

    handles = set()
    # split the message by @ and exclude the first word 
    # as it is not after a '@'
    for word in re.split('@', message)[1:]:
        # the first word after @ will be the potential handle
        handle = re.split(regular_exp, word)[0]
        if handle != '' and valid_handle(handle):
            handles.add(handle)
           
    for handle in handles:
        u_id = handle_to_id(handle)
        # make sure the user who tagged is in either channel or dm
        if user_in_channel_dm(u_id, channel_id, dm_id):
            name = get_name(channel_id, dm_id)
            for user in store['users']:
                if user['user_id'] == u_id:
                    notification = f'{get_handle(auth_user_id)} tagged you in {name}: {message[0:20]}'
                    note = {
                        'channel_id': channel_id,
                        'dm_id': dm_id,
                        'notification_message': notification
                    }
                    user['notifications'].insert(0, note)
    
# add to a user's notification from reacting to a message
def notification_react(auth_user_id, user_id, channel_id, dm_id):
    store = data_store.get()
    handle = get_handle(user_id)
    name = get_name(channel_id, dm_id)
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            notification = f'{handle} reacted to your message in {name}'
            note = {
                        'channel_id': channel_id,
                        'dm_id': dm_id,
                        'notification_message': notification
            }
            user['notifications'].insert(0, note)

# add to a user's notification from adding to either a channel or dm
def notification_add(auth_user_id, user_id, channel_id, dm_id):
    store = data_store.get()
    handle = get_handle(user_id)
    name = get_name(channel_id, dm_id)
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            notification = f'{handle} added you to {name}'
            note = {
                        'channel_id': channel_id,
                        'dm_id': dm_id,
                        'notification_message': notification
            }
            user['notifications'].insert(0, note)

