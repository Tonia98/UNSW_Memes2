import requests
from src.channels import token_to_id
from src.data_store import data_store
from src.dm import valid_dm
from src.error import *
from datetime import timezone, datetime
from src.config import url
import math 
from src.stats import *
import threading
import time
from src.notifications import notification_react, notification_tag

#check if the channel_id exists in the data_store
def valid_channel(channels, channel_id):
    
    for channel in channels:
        if channel['channel_id'] == channel_id:
            return True
    return False


def create_message(auth_user_id, message, message_id):
    # getting tiomestamp through datetime libary
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    # returns details in each message send
    return {
        'message_id': message_id, 
        'u_id': auth_user_id,
        'message': message,
        'time_created': timestamp,
        'reacts':[{
                'react_id': 1,
                'u_ids':[],
                'is_this_user_reacted': False,
        }],
        'is_pinned': False
        
    }
def valid_user_in_channel(auth_user_id, channel_id):
    store = data_store.get() 
    channels = store['channels'] 
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user_id not in channel['all_members']:
                return False
            else:
                return True

def valid_user_in_dm(auth_user_id, dm_id):
    store = data_store.get()
    dms = store['dms']
    for dm in dms:
        if dm['dm_id'] == dm_id:
            if auth_user_id not in dm['members']:
                return False
            else:
                return True
################################ itertion 3 ########################################
# check whether the user has permission to share/react to the message
def check_valid_message_id(auth_user_id, message_id):
    store = data_store.get()
    
    # get the message in channel
    for channel in store['channels']:
        for message in channel['messages']:
            # check if the user is in channel
            if message['message_id'] == message_id:
                if auth_user_id in channel['all_members']:
                    return
                else:
                    raise InputError('user not in the channel which the message is in')
            
                
    # get the message in dm
    for dm in store['dms']:
        for message in dm['messages']:
            # check if the user is in dm
            if message['message_id'] == message_id:
                if auth_user_id in dm['members']:
                    return
                else:
                    raise InputError('user not in the dm which the message is in')
            
    raise InputError('message_id is not valid')
    
    # message is not found
    
                


def message_share(token, og_message_id, message, channel_id, dm_id):
    '''
    share a message into another channel or dm that the user has joined
    
    Arguments:
        token(string) - the token of an user
        og_message_id - the original message id
        message(string) - the message that user wants to add to existing message
        channel_id(int) - the id of a channel
        dm_id(int) - the id of a dm
        
    Exceptions:
        InputError 
        - Occurs when both channel_id and dm_id are invalid
        - Occurs when neither channel_id nor dm_id are -1
        - og_message_id does not refer to a valid message within a channel/DM that the user has joined
        - Occurs when length of message is less than 1 or over 1000 characters
        AccessError
        - Occurs when the pair of channel_id and dm_d are valid, and the authorised user has not joined 
          the channel or DM they are trying to share the message to
    
    Return Value:
        Returns a shared_message_id 
    '''
    
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    if valid_user_in_channel(auth_user_id, channel_id) == False or valid_user_in_dm(auth_user_id, dm_id) == False:
        raise AccessError("Invalid user accessing")
    # check if the given message_id is valid
    check_valid_message_id(auth_user_id, og_message_id)
    # check if both channel_id and dm_id are not equal to 1
    if channel_id != -1 and dm_id != -1:
        raise InputError("Invalid sharing destination")
    # check if both channel_id and dm_id are valid
    if valid_channel(store['channels'],channel_id) == False and valid_dm(store['dms'],dm_id) == False:
        raise InputError("Invalid channel id and dm id")
    # check if the length of message is valid
    if len(message) > 1000:
        raise InputError("Invalid message length")
    
    
    # loop through to find which message to share
    for channel in channels:
        for message_share in channel['messages']:
            # check if the given message_id exists
            if message_share['message_id'] == og_message_id:
                temp_message = message_share['message'] + message
                dt = datetime.now()
                timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
                # update to new timestamp
                message_share['time_created'] = timestamp
                message_id = store['message_id_tracker']
                store['message_id_tracker'] += 1
                # store new shared message into temp
                temp = create_message(auth_user_id, temp_message, message_id)       
    
    
    for dm in dms:
        for message_share in dm['messages']:
            # check if the given message_id exists
            if message_share['message_id'] == og_message_id:
                temp_message = message_share['message'] + message
                dt = datetime.now()
                timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp()) 
                # update to new timestamp
                message_share['time_created'] = timestamp
                message_id = store['message_id_tracker']
                store['message_id_tracker'] += 1
                # store new shared message into temp
                temp = create_message(auth_user_id, temp_message, message_id)
    
    # if the message is sharing to channel
    if dm_id == -1:
        for channel in channels:
            if channel['channel_id'] == channel_id:
                # insert new shared message into destination
                channel['messages'].insert(0, temp)
                # call other functions for further actions
                user_stats_add_message(auth_user_id)
                stream_stats_add_message()
                notification_tag(auth_user_id, channel['channel_id'], -1, temp['message'])
                return {
                    'shared_message_id': message_id
                }
    
    # if the message is sharing to dm
    if channel_id == -1:
        for dm in dms:
            if dm['dm_id'] == dm_id:
                # insert new shared message into destination
                dm['messages'].insert(0, temp) 
                # call other functions for further actions
                user_stats_add_message(auth_user_id)
                stream_stats_add_message()
                notification_tag(auth_user_id, -1, dm['dm_id'], temp['message'])
                return {
                    'shared_message_id': message_id
                }
   
def message_react(token, message_id, react_id):
    '''
    react to a message as a user in channel or dm
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        react_id(int) - the id of a react instruction
        
    Exceptions:
        InputError 
        - Occurs when message_id does not refer to a valid message within a channel or dm
          that the authorised user has joined
        - Occurs when react_id is not a valid react_id
        - the message already contain a react with ID react_id from the authroised user
        
    
    Return Value:
        Returns an empty dictionary
    '''
    
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    # check if the given message_id is valid
    check_valid_message_id(auth_user_id, message_id)
    # check if react_id is valid
    if react_id != 1:
        raise InputError("Invalid react_id")
    
    for channel in channels:
        for message_pre in channel['messages']:
            # check if message_id and user is in the channel
            if message_pre['message_id'] == message_id and auth_user_id in channel['all_members']:
                react = message_pre['reacts'][0]
                # if user has already reacted to this message an InputError will be raise
                if auth_user_id in react['u_ids']:
                    raise InputError("User has already reacted to this message")
                # add user_id into react list
                react['u_ids'].append(auth_user_id)
                notification_react(message_pre['u_id'], auth_user_id, channel['channel_id'], -1)
                return {}
            
                    
    for dm in dms:
        for message in dm['messages']:
            # check if the given message_id is in DM
            if message['message_id'] == message_id and auth_user_id in dm['members']:
                react = message['reacts'][0]
                # if user has alaready reacted to this message an InputError will be raise 
                if auth_user_id in react['u_ids']:
                    raise InputError("User has already reacted to this message")
                # add user_id into react list
                react['u_ids'].append(auth_user_id)
                notification_react(message['u_id'], auth_user_id, -1, dm['dm_id'])
                return {}
                


def message_unreact(token, message_id, react_id):
    '''
    unreact to a message that the user(token) has reacted to previously
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        react_id(int) - the id of a react instruction
        
    Exceptions:
        InputError 
        - Occurs when message_id does not refer to a valid message within a channel or dm
          that the authorised user has joined
        - Occurs when react_id is not a valid react_id
        - the message does not contain a react with ID react_id from the authroised user
        
    
    Return Value:
        Returns an empty dictionary
    '''

    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    channel = store['channels']
    
    check_valid_message_id(auth_user_id, message_id)
    # check if react_id is valid
    if react_id != 1:
        raise InputError("Invalid react_id")

    for channel in channels:
        for message_pre in channel['messages']:
            # check if the given message_id is in channel
            if message_pre['message_id'] == message_id and auth_user_id in channel['all_members']:
                react = message_pre['reacts'][0]
                if auth_user_id not in react['u_ids']:
                    raise InputError("User has not react to this message")
                # removes a user from the react list
                react['u_ids'].remove(auth_user_id)
                if react['u_ids'] == []:
                    react['is_this_user_reacted'] = False
                return {}

                    
    for dm in dms:
        for message in dm['messages']:
            # check if the given message_id exists
            if message['message_id'] == message_id and auth_user_id in dm['members']:
                react = message['reacts'][0]
                if auth_user_id not in react['u_ids']:
                    raise InputError("User has not react to this message")
                # removes a user from the react list
                react['u_ids'].remove(auth_user_id)
                if react['u_ids'] == []:
                    react['is_this_user_reacted'] = False
                return {}
    

################################ itertion 2 ########################################
def message_send(token, channel_id, message):
    
    '''
    send message into the channel given valid token, channel_id and message
    
    Arguments:
        token(string) - the token of an user
        channel_id(int) - the id of a channel
        message(string) - the message that user wants to send into the channel
        
    Exceptions:
        InputError 
        - Occurs when channel_id is not valid id in data_store
        - Occurs when length of message is less than 1 or over 1000 characters
        AccessError
        - Occurs when channel_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns a message_id 
    '''
    
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    # check if channel_id is valid
    if valid_channel(store['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
    
    for channel in channels:
        # find the matching channel in data_store with input channel_id from the user
        if channel['channel_id'] == channel_id:
            # check if user_id belongs to the given channel_id
            if auth_user_id not in channel['all_members']:
                raise AccessError("Valid channel_id but invalid user_id")
            # check if the length of message is valid
            if len(message) == 0 or len(message) > 1000:
                raise InputError("does not match the required length")
            
            # import message_id_tracker from data_store to ensure no other message share the same id
            message_id = store['message_id_tracker']
            store['message_id_tracker'] += 1
            # insert the newest message at the beginning of message list
            channel['messages'].insert(0, create_message(auth_user_id, message, message_id))
    user_stats_add_message(auth_user_id)
    stream_stats_add_message()
    notification_tag(auth_user_id, channel_id, -1, message)
    return {
        'message_id': message_id
    }

def valid_messge_id_invalid_user(auth_user_id, message_id):
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    
    permission = get_user_permission(auth_user_id)

    for channel in channels:
        for message_pre in channel['messages']:
            # check if the given message_id exists
            if message_pre['message_id'] == message_id:
                # check if the user has access to modify messages in the channel
                if message_pre['u_id'] != auth_user_id and permission != 1 and auth_user_id not in channel['owner_members']:
                    raise AccessError("message was not sent by the authorised user")
                else:
                    return
                    
    for dm in dms:
        for message in dm['messages']:
            # check if the given message_id exists
            if message['message_id'] == message_id:
                # check if the user has access to modify messages in dm
                if message['u_id'] != auth_user_id and auth_user_id != dm['creator']:
                    raise AccessError("message was not sent by the authorised user")
                else:
                    return

    # raise inputerror when the given message_id is invalid
    raise InputError("Invalid message_id")
    
# ------------------------- < message edit > ----------------------------
def message_edit(token, message_id, message):
    
    '''
    edit existing message in channel for dms
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        message(string) - the message that user wants to send into the channel
        
    Exceptions:
        InputError 
        - Occurs when message_id does not refer to a valid message within a channel or dm
        - Occurs when length of message is over 1000 characters
        AccessError (when message_id are valid)
        - Occurs when the message was not sent by the authorised user making this request
        - Occurs when the authorised user does not have owner permissions in the channel or dm
    
    Return Value:
        Returns an empty dictionary
    '''

    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    
    # check if user and message_id are valid
    valid_messge_id_invalid_user(auth_user_id, message_id)

    check_valid_message_id(auth_user_id, message_id)
    # removes the message when an empty string is given
    if len(message) == 0:
        message_remove(token, message_id)
    
    # check if the message length of updated message is valid
    if len(message) > 1000:
        raise InputError("Invalid message length")
    
    # edit message in channel
    for channel in channels:
        for message_pre in channel['messages']:
            if message_pre['message_id'] == message_id:
                # replace the new message with the old message
                message_pre['message'] = message
                notification_tag(auth_user_id, channel['channel_id'], -1, message)

    # edit message in dm                
    for dm in dms:
        for message_pre_dm in dm['messages']:
            if message_pre_dm['message_id'] == message_id:    
                # replace the new message with the old message    
                message_pre_dm['message'] = message
                notification_tag(auth_user_id, -1, dm['dm_id'], message)
    
    
    return {}

# ------------------------- < message remove > ----------------------------

def message_remove(token, message_id):
    
    '''
    remove a message in channel or dm given a valid token and message_id
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        
        
    Exceptions:
        InputError 
        - Occurs when message_id does not refer to a valid message within a channel or dm
        
        AccessError (when message_id are valid)
        - Occurs when the message was not sent by the authorised user making this request
        - Occurs when the authorised user does not have owner permissions in the channel or dm
    
    Return Value:
        Returns an empty dictionary
    '''
    
    auth_user_id = token_to_id(token)
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    
    # check if user and message_id are valid
    valid_messge_id_invalid_user(auth_user_id, message_id)

    check_valid_message_id(auth_user_id, message_id)
    # removes message in channel
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                # removes messages and its details
                channel['messages'].remove(message)

    # removes message in dm
    for dm in dms:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                # removes messages and its details        
                dm['messages'].remove(message)
    stream_stats_remove_message()
    return {}

def message_senddm(token, dm_id, message):
    
    '''
    send direct message to users in dm
    
    Arguments:
        token(string) - the token of an user
        dm_id(int) - the id of a dm
        message(string) - the message that user wants to send into the channel
        
    Exceptions:
        InputError 
        - Occurs when dm_id does not refer to a valid dm
        - Occurs when length of message is less than 1 or over 1000 characters
        AccessError (when message_id are valid)
        - Occurs when dm_id is valid and the authorised user is not a member of the dm
    
    Return Value:
        Returns a message_id
    '''

    auth_user_id = token_to_id(token)
    store = data_store.get()
    
    dms = store['dms']
    for dm in dms:
        # find the matching channel in data_store with input dm_id from the user
        if dm['dm_id'] == dm_id:
            # check if user_id belongs to the given dm_id
            if auth_user_id not in dm['members']:
                raise AccessError("Valid dm_id but invalid user_id")
            
            if len(message) == 0 or len(message) > 1000:
                raise InputError("does not match the required length")
            
            # import message_id_tracker from data_store to ensure no other message share the same id
            message_id = store['message_id_tracker']
            store['message_id_tracker'] += 1

            # insert the newest message at the beginning of message list
            dm['messages'].insert(0, create_message(auth_user_id, message, message_id))

    # check if the given dm_id is valid
    if valid_dm(store['dms'],dm_id) == False:
        raise InputError("Invalid dm id")
    user_stats_add_message(auth_user_id)
    stream_stats_add_message()
    notification_tag(auth_user_id, -1, dm_id, message)
    return {
        'message_id': message_id
    }


#---------------------- message pin and unpin ----------------------------------

def get_the_message(message_id):
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']

    message_index = 0
    channel_index = 0
    # find th message index if the message is in the channel, if finded, True is asserted to is_channel
    for channel in channels:
        message_index = 0
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return (message_index, True, channel_index)
            message_index += 1
        channel_index += 1
        
    # find th message index if the message is in the dm, if finded, False is asserted to is_channel
    dm_message_index = 0
    dm_index = 0
    for dm in dms:
        dm_message_index = 0
        for message in dm['messages']:
            if message['message_id'] == message_id:
                return (dm_message_index, False, dm_index)
            dm_message_index += 1
        dm_index += 1

    # if not finded, not found is assigned to message index
    return ('not found', False, False)

def get_user_permission(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            return user['permission']

def check_message_id_and_user_has_owner_permission(message_id, user_id):
    
    (message_index, is_channel, cdm_index) = get_the_message(message_id)
    permission = get_user_permission(user_id)

    store = data_store.get()
    
    # This function checks if channel messsage is exsist or not
    # If message exist, it also checks if auth user is in this channel or dm

    if is_channel:
        if (message_index == 'not found') or (user_id not in store['channels'][cdm_index]['all_members']):
            raise InputError('message id not found or auth_user not in this channel')
        elif permission != 1 and (user_id not in store['channels'][cdm_index]['owner_members']):
            raise AccessError('valid message id, but user does not have owner permission in this channel')
    
    if (not is_channel):
        if (message_index == 'not found' or user_id not in store['dms'][cdm_index]['members']):
            raise InputError('message id not found or auth_user not in this dm')
        elif (user_id != store['dms'][cdm_index]['creator']):
            raise AccessError('valid message id, but user does not have owner permission in this dm')
    
def message_pin(token, message_id):
    '''
    pin a message
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        
    Exceptions:
        InputError 
        - Occurs when message id is invalid that auth user has joined
        - Occurs when message is already pinned
        AcessError
        - Occurs when message id is a valid message but auth user does not have owner permission
    Return Value:
        {}
    '''
    store = data_store.get()
    auth_user_id = token_to_id(token)
    (message_index, is_channel, cdm_index) = get_the_message(message_id)
    check_message_id_and_user_has_owner_permission(message_id, auth_user_id)

    # This part checks if the message is pinned or not , if it is not pinned, pin it
    if is_channel:
        if store['channels'][cdm_index]['messages'][message_index]['is_pinned']:
            raise InputError('the message is already pinned')
        else:
            store['channels'][cdm_index]['messages'][message_index]['is_pinned'] = True
    else:
        if store['dms'][cdm_index]['messages'][message_index]['is_pinned']:
            raise InputError('the message is already pinned')
        else:
            store['dms'][cdm_index]['messages'][message_index]['is_pinned'] = True

    return {}

def message_unpin(token, message_id):
    '''
    unpin a message
    
    Arguments:
        token(string) - the token of an user
        message_id(int) - the id of a message
        
    Exceptions:
        InputError 
        - Occurs when message id is invalid that auth user has joined
        - Occurs when message is already unpinned
        AcessError
        - Occurs when message id is a valid message but auth user does not have owner permission
    Return Value:
        {}
    '''
    store = data_store.get()
    auth_user_id = token_to_id(token)
    (message_index, is_channel, cdm_index) = get_the_message(message_id)
    check_message_id_and_user_has_owner_permission(message_id, auth_user_id)

    # This part checks if the message is pinned or not , if it is pinned, unpin it
    if is_channel:
        if not store['channels'][cdm_index]['messages'][message_index]['is_pinned']:
            raise InputError('the message is already not pinned')
        else:
            store['channels'][cdm_index]['messages'][message_index]['is_pinned'] = False
    else:
        if not store['dms'][cdm_index]['messages'][message_index]['is_pinned']:
            raise InputError('the message is already not pinned')
        else:
            store['dms'][cdm_index]['messages'][message_index]['is_pinned'] = False

    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''
    send message at time_sent time in a channel
    
    Arguments:
        token(string) - the token of an user
        channel_id(int) - the id of a channel
        message(string) - the message that user wants to send into the channel
        time_sent(integer) - the time the user want to send the message

    Exceptions:
        InputError 
        - Occurs when channel_id is invalid
        - Occurs when length of message is over 1000 characters
        - Occurs when time_sent is a time in the past
        AccessError
        - Occurs when channel_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns a message_id 
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()

    if valid_channel(store['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
    
    message_id = store['message_id_tracker']

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            # check if the user is in this channel
            if auth_user_id not in channel['all_members']:
                raise AccessError('valid channel id, but user is not in this channel')
            
            if len(message) == 0 or len(message) > 1000:
                raise InputError("does not match the required length")

            # get the time of now, then calculate the difference betetween now and
            # user wanted to send time, then send the message after 'the difference time'
            dt = datetime.now()
            now_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
            sent_time = datetime.fromtimestamp(time_sent)
            raw_time_difference = sent_time - datetime.fromtimestamp(now_timestamp)
            time_difference = raw_time_difference.total_seconds()
            if time_difference < 0:
                raise InputError('time_sent is a time in the past')
            t = threading.Timer(time_difference, message_send, [token, channel_id, message])
            t.start()       
    return {'message_id': message_id}

def message_sendlaterdm(token, dm_id, message, time_sent):
    '''
    send message at time_sent time in a channel
    
    Arguments:
        token(string) - the token of an user
        dm_id(int) - the id of a dm
        message(string) - the message that user wants to send into the dm
        time_sent(integer) - the time the user want to send the message

    Exceptions:
        InputError 
        - Occurs when dm_id is invalid 
        - Occurs when length of message is over 1000 characters
        - Occurs when time_sent is a time in the past
        AccessError
        - Occurs when dm_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns a message_id 
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()

    if valid_dm(store['dms'],dm_id) == False:
        raise InputError("Invalid dm id")
    
    message_id = store['message_id_tracker']

    dms = store['dms']
    for dm in dms:
        # find the matching channel in data_store with input dm_id from the user
        if dm['dm_id'] == dm_id:
            # check if user_id belongs to the given dm_id
            if auth_user_id not in dm['members']:
                raise AccessError("Valid dm_id but invalid user_id")
            
            if len(message) == 0 or len(message) > 1000:
                raise InputError("does not match the required length")

            # get the time of now, then calculate the difference betetween now and
            # user wanted to send time, then send the message after 'the difference time'
            dt = datetime.now()
            now_timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
            sent_time = datetime.fromtimestamp(time_sent)
            raw_time_difference = sent_time - datetime.fromtimestamp(now_timestamp)
            time_difference = raw_time_difference.total_seconds()
            if time_difference < 0:
                raise InputError('time_sent is a time in the past')
            t = threading.Timer(time_difference, message_senddm, [token, dm_id, message])
            t.start()    

    return {'message_id': message_id}      

