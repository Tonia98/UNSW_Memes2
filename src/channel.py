from src.channels import token_to_id
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import requests
import re
from src.config import url
from src.stats import *
from src.notifications import notification_add

# ------------------------------------- < channel_invite > ----------------------------------------

# Invites a user with ID u_id to join a channel with ID channel_id. Once invited, 
# the user is added to the channel immediately. In both public and private channels, 
# all members are able to invite users.

def channel_invite(token, channel_id, u_id):
    '''
<Invites a user with ID u_id to join a channel with ID channel_id>

Arguments:
    <auth_user_id> (integer)    - <Someone who invites others to join a channel>
    <channel_id> (integer)    - <Channel id that auth_user Invites u_id to join>
    <u_id> (integer)    - <Id of the invitee>

Exceptions:
    InputError  - Occurs when 1）channel_id does not refer to a valid channel.
                              2）u_id does not refer to a valid user
                              3）u_id refers to a user who is already a member of the channel
    AccessError - Occurs when 1）channel_id is valid and the authorised user is not a member of the channel

Return Value:
    {}
'''
    auth_user_id = token_to_id(token)
    valid_channel = False
    valid_user = False
    already_in = False
    valid_auth_id = False
    # importing a Database
    store = data_store.get()
    
    # valid u_id
    for user in store['users']:
        if user['user_id'] == u_id:
            valid_user = True

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            valid_channel = True
            for user_id in channel['all_members']:
            # Check whether the authorised user is a member of the channel
                if user_id == auth_user_id:
                    valid_auth_id = True

                # CHeck whether u_id refers to a user who is already a member of the channel
                if user_id == u_id:
                    already_in = True
            # the valid situation
            if valid_auth_id == True and already_in == False and valid_user == True:
                channel['all_members'].append(u_id)
                user_stats_add_channel(u_id)
                notification_add(u_id, auth_user_id, channel_id, -1)
                
                    
    if valid_channel == True and valid_auth_id == False:
        raise AccessError("Valid channel but the authorised user is not in the channel")

    if already_in == True:
        raise InputError("u_id refers to a user who is already a member of the channel")

    if valid_user == False:
        raise InputError("u_id does not refer to a valid user")
    
    # Check InputError: check whether refer to a valid channel
    if valid_channel == False:
        raise InputError("channel_id does not refer to a valid channel")

    return {}
    


    


# ------------------------------------- < channel_details> ----------------------------------------

#check if the channel_id exists in the data_store
def valid_channel(channels, channel_id):
    for channel in channels:
        
        if channel['channel_id'] == channel_id:
            return True
    return False

#check if the user is a member of the channel
def auth_user(user, allmembers):
    if user in allmembers:
        return True
    return False

# transform the dictionary of a user in data store
# to the format matching the output of the channel_details()
def transform_dict_user(user):
    return {
        'u_id':user['user_id'],
        'email':user['email'],
        'name_first':user['name_first'],
        'name_last':user['name_last'],
        'handle_str':user['handle'],
        'profile_img_url':user['profile_img_url']
    }

# transform the dictionary of a channel in data store
# to the format matching the output of the channel_details()
def transform_dict_channel(channel):
    data = data_store.get()
    owners = []
    for user in data['users']:
        if user['user_id'] in channel['owner_members']:
            owners.append(transform_dict_user(user))
            
    alls = []
    for user in data['users']:
        if user['user_id'] in channel['all_members']:
            alls.append(transform_dict_user(user))
    
    return {
        'name': channel['channel_name'],
        'owner_members':owners,
        'all_members':alls,
        'is_public':channel['is_public']

    }


def channel_details(token, channel_id):

    '''
    use channel_id and auth_user_id to provide basic details about the channel 

    Arguments:
        token(string) - an encoded string contains the user_id and session_id of an user
        channel_id(int) - the id of a channel
        
    Exceptions:
        InputError - Occurs when channel_id is not valid(not in the data store)
        AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns a dictionary which contains basic details about the channel 
    '''

    data1 = data_store.get()
    '''
    #test valid user
    if valid_user(data1['users'], token) == False:
        raise AccessError("Invalid user token") #check!!!!!
    '''

    auth_user_id = token_to_id(token)
    #test valid channel
    if valid_channel(data1['channels'],channel_id) == False:
        raise InputError("Invalid channel")
    
    # loop through to find the targeted channel
    for channel in data1['channels']:
        if channel['channel_id'] == channel_id:
            if auth_user(auth_user_id, channel['all_members']) == False:
                raise AccessError('Unauthorised user')
            else:
                channel_details = transform_dict_channel(channel)
            return channel_details


# ------------------------------------- < channel_messages> ----------------------------------------

# create a list of dictionary for message in data store
def transform_dict(auth_user_id, channel, start):
    '''
    transform the message's dictionary stored in the data store (empty list)
    to the output form channel_messages() function
    
    Arguments:
        channel(messages) - a dictionary contains 
        messages:{
            'message_id'
            'u_id'
            'message'
            'time_created'
            'is_pinned'
        }
        'start'
        'end'

    
    Return Value:
        Returns a dictionary contains 'messages', 'start' and 'end'
    '''

    new_message_list = []
    # access message form channel in data_store
    messages = channel['messages']
    start_id = start
    i = 1
    while i <= 50:
        # check if least recent message is being read
        if start_id == len(channel['messages']):
            break
        messages[start_id]['reacts'][0]['is_this_user_reacted'] = False
        if auth_user_id in messages[start_id]['reacts'][0]['u_ids']:
            messages[start_id]['reacts'][0]['is_this_user_reacted'] = True
        # append message from the most recent to the least bewteen start_id and start_id + 50
        new_message_list.append(messages[start_id])
        start_id += 1
        i += 1
    # if not all messages are read
    if len(channel['messages']) >= start + 50:
        end = start + 50
    # if most recent messages have been read
    else:
        end = -1
    return {
        'messages': new_message_list,
        'start': start,
        'end': end,
    }


def channel_messages(token, channel_id, start):
    '''
    Read at most 50 messages from 'start' index for user in a particular channel
    
    Arguments:
        auth_user_id(int) - the id of an user
        channel_id(int) - the id of a channel
        start(int) - starting position of reading messages in data_store (from most recent message)
        
    Exceptions:
        InputError 
        - Occurs when channel_id is not valid id in data_store
        - Occurs when 'start' index is greater than the numebr of messages in data_store
        AccessError
        - Occurs when channel_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns a list of dictionaries of messages being read from the starting index alongside with
        the position of starting and ending index
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    
    
    # creating empty list for returning message dictionary
    message_list = {}
    '''
    # check if user_id exist in data_store
    if valid_user(store['users'],auth_user_id) == False:
        raise AccessError("Can not find the user, invalid user_id")
    '''
    # loop through every channel in data_store
    for channel in channels:
        # find the matching channel in data_store with input channel_id from the user
        if channel['channel_id'] == channel_id:
            # check if user_id belongs to the given channel_id
            if auth_user_id not in channel['all_members']:
                raise AccessError("Valid channel_id but invalid user_id")

            # check if start_index is bigger than the number of message stored in data_store
            if (start > len(channel['messages'])):
                raise InputError("Invalid starting postion")
            
            # import list of messages from transform_dict founction
            message_list = transform_dict(auth_user_id, channel, start)
    
    # check if channel_id is valid
    if valid_channel(store['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
        
    return message_list

# ------------------------------------- < channel_join> ----------------------------------------
def channel_join(token, channel_id):
    '''
<Given a channel_id of a channel that the authorised user can join, adds them to that channel.>

Arguments:
    <auth_user_id> (integer)    - <Someone will join into channel>
    <channel_id> (integer)    - <Channel id that auth_user will join>

Exceptions:
    InputError  - Occurs when 1）channel_id does not refer to a valid channel
                              2）the authorised user is already a member of the channel
                              
    AccessError - Occurs when 1）channel_id refers to a channel that is private and the authorised user 
                                 is not already a channel member and is not a global owner

Return Value:
    {}

'''
    auth_user_id = token_to_id(token)
    valid_channel = False
    permission = 0
    already_in = False
    # importing a Database
    store = data_store.get()

    for user in store['users']:
        if user['user_id'] == auth_user_id:
            permission = user['permission']

    # Find the appropriate channel and insert the user_id
    for channel in store['channels']:
        # Check InputError: Check whether authorised user is already in the channel
        if channel['channel_id'] == channel_id:
            # Check Access Error
            for members in channel['all_members']:
                if members == auth_user_id:
                    already_in = True
                # Check whether channel is private and authorised user is not already a channel member 
                # and is not a global owner 
            if (channel['is_public'] == False and permission != 1): 
                    raise AccessError("channel that is private and the  user is not a channel member and is not a global owner")

            valid_channel = True
            channel['all_members'].append(auth_user_id)
            user_stats_add_channel(auth_user_id)
    
    # Check InputError: check whether refer to a valid channel
    if (valid_channel == False):
        raise InputError("channel_id does not refer to a valid channel")
    if already_in == True:
        raise InputError("the authorised user is already a member of the channel")

    return {}


def channel_leave(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in the channel. 
    If the only channel owner leaves, the channel will remain.>

Arguments:
    <token> (string) - an encoded string contains the user_id of a user
    <channel_id> (integer)    - <Channel id that owner will leave>


Exceptions:
    InputError  - channel_id does not refer to a valid channel

    AccessError - channel_id is valid and the authorised user is not a member of the channel
    
Return Value:
    Returns {}
    '''
    # Seek auth_user_id
    auth_user_id = token_to_id(token)
    valid_channel = False
    channel_member = False
    # importing a Database
    store = data_store.get()

    for channel in store['channels']:
        # Check whether is a valid channel
        if channel['channel_id'] == channel_id:
            valid_channel = True

        for members in channel['all_members']:
            if auth_user_id == members:
                channel_member = True
    
    # Do Access Error Checking
    # (An Access error is checked first because it has a higher priority than an input error)
    if (valid_channel == True and channel_member == False):
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

    # Do Input Error Checking
    if (valid_channel == False):
        raise InputError("channel_id does not refer to a valid channel")

    for channel in store['channels']:
        # Check whether is a valid channel
        if channel['channel_id'] == channel_id:
            channel['all_members'].remove(auth_user_id)
            user_stats_remove_channel(auth_user_id)
            # Check whether user is a owner, if so, remove them as a owner
            for owners in channel['owner_members']:
                if owners == auth_user_id:
                    channel['owner_members'].remove(auth_user_id)

def channel_addowner(token, channel_id, u_id):
    '''
    <Make user with user id u_id an owner of the channel.>

Arguments:
    <token> (string) - an encoded string contains the user_id of a user
    <channel_id> (integer)    - <Channel id that owner will add>
    <u_id> (integer)    - <Id that people will add>

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                              u_id does not refer to a valid user
                              u_id refers to a user who is not a member of the channel
                              u_id refers to a user who is already an owner of the channel
                              

    AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
    
Return Value:
    Returns {}
    '''
    # Seek auth_user_id
    auth_user_id = token_to_id(token)

    valid_channel = False
    valid_uid = False
    channel_member = False
    inviter_member = False
    channel_owner = False
    global_permission = False
    channel_permission = False
    # importing a Database
    store = data_store.get()

    for channel in store['channels']:
        # Check whether is a valid channel
        if channel['channel_id'] == channel_id:
            valid_channel = True
            if u_id in channel['all_members']:
                channel_member = True
            if u_id in channel['owner_members']:
                channel_owner = True
            # Check if auth user has channel owner permission
            if auth_user_id in channel['owner_members']:
                channel_permission = True
            if auth_user_id in channel['all_members']:
                inviter_member = True
            
    
    for user in store['users']:
        # Check whether is a valid u_id
        if user['user_id'] == u_id:
            valid_uid = True
        # Check whether authorised user have owner permissions
        if user['user_id'] == auth_user_id and user['permission'] == 1 and inviter_member == True:
            global_permission = True

    # Do Access Error Checking
    # (An Access error is checked first because it has a higher priority than an input error)
    if (valid_channel == True and global_permission == False and channel_permission == False):
        raise AccessError("channel_id is valid and the authorised user does not have owner permissions in the channel")
    
    # Do Input Error Checking
    if (valid_channel == False):
        raise InputError("channel_id does not refer to a valid channel")

    if (valid_uid == False):
        raise InputError("u_id does not refer to a valid user")

    if (channel_member == False):
        raise InputError("u_id refers to a user who is not a member of the channel")
    
    if (channel_owner == True):
        raise InputError("u_id refers to a user who is already an owner of the channel")        


    # Make user with user id u_id an owner of the channel.
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['owner_members'].append(u_id)


def channel_removeowner(token, channel_id, u_id):
    '''
    <Remove user with user id u_id as an owner of the channel.>

Arguments:
    <token> (string) - an encoded string contains the user_id of a user
    <channel_id> (integer)    - <Channel id that owner will remove>
     <u_id> (integer)    - <Id that people will remove>

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                              u_id does not refer to a valid user
                              u_id refers to a user who is not an owner of the channel
                              u_id refers to a user who is currently the only owner of the channel

    AccessError - Occurs when channel_id is valid and the authorised user does not have owner permissions in the channel

Return Value:
    Returns {}
    '''

    # Seek auth_user_id
    auth_user_id = token_to_id(token)

    valid_channel = False
    channel_owner = False
    channel_member = False
    only_owner = False
    global_permission = False
    channel_permission = False
    valid_uid = False
    # importing a Database
    store = data_store.get()

    for channel in store['channels']:
        # Check whether is a valid channel
        if channel['channel_id'] == channel_id:
            valid_channel = True
            # Check if auth user has channel owner permission
            if auth_user_id in channel['owner_members']:
                channel_permission = True
            if auth_user_id in channel['all_members']:
                channel_member = True
            # Check whether u_id is a channel owner
            if u_id in channel['owner_members']:
                channel_owner = True
                # Check whether u_id the only channel owner
                if len(channel['owner_members']) == 1:
                    only_owner = True

    for user in store['users']:
        # Check whether is a valid u_id
        if user['user_id'] == u_id:
            valid_uid = True
        # Check whether authorised user have owner permissions
        if user['user_id'] == auth_user_id and user['permission'] == 1 and channel_member == True:
            global_permission = True

    # Do Access Error Checking
    # (An Access error is checked first because it has a higher priority than an input error)
    if (valid_channel == True and global_permission == False and channel_permission == False):
        raise AccessError("channel_id is valid and the authorised user does not have owner permissions in the channel")

    # Do Input Error Checking
    if (valid_channel == False):
        raise InputError("channel_id does not refer to a valid channel")

    if (valid_uid == False):
        raise InputError("u_id does not refer to a valid user")
    
    if (channel_owner == False):
        raise InputError("u_id refers to a user who is not an owner of the channel")

    if (only_owner == True):
        raise InputError("u_id refers to a user who is currently the only owner of the channel")

    
    # Remove user with user id u_id as an owner of the channel.
    for channel in store['channels']:
        # Check whether is a valid channel
        if channel['channel_id'] == channel_id:
            channel['owner_members'].remove(u_id)
    

