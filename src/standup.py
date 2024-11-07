from _pytest.fixtures import PseudoFixtureDef
from src.channels import * #token to id 
from src.channel import * #auth_user
from src.message import * #create message,valid_channel
from src.data_store import *
from src.config import url
from src.message import *
from src.error import *
import datetime 
from datetime import *
import threading
from src.stats import *

    

#the function will run after the waiting length seconds
def stop_send(auth_user_id,channel_id):
    data = data_store.get()
    channels = data['channels']
    for channel in channels:
        if channel['channel_id'] == channel_id:
            channel['is_active'] = False
            messages = channel['messages']
            messages.insert(0,{
                'message_id': data['message_id_tracker'],
                'u_id': auth_user_id ,
                'message': channel['standups'],
                'time_created': channel['time_finish'],
                'reacts':[{
                    'react_id': 1,
                    'u_ids':[],
                    'is_this_user_reacted': False,
                }],
                'is_pinned': False
            })
            channel['standups'] = ''
            channel['time_finish'] = None
            data['message_id_tracker'] += 1
            user_stats_add_message(auth_user_id)
            stream_stats_add_message()




def standup_start(token, channel_id, length):
    '''
    start the standup period length
    if someone calls "standup/send" with a message and send message at the end of the X second
    Arguments:
        token(string) - the token of an user
        channel_id(int) - the id of a channel
        length(int) - the second of time waited
        
    Exceptions:
        InputError 
        - Occurs when channel_id is not valid id in data_store
        - Occurs when length is a negative integer
        - Occurs when an active standup is currently running in the channel
        AccessError
        - Occurs when channel_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns is active and the time finish(the standup)
    '''
    auth_user_id = token_to_id(token)
    data = data_store.get()
    channels = data['channels']

    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user(auth_user_id, channel['all_members']) == False:
                raise AccessError('Unauthorised user')
    
    if valid_channel(data['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
    
    if length < 0:
        raise InputError('Negative time length')

    for channel in channels:
        if channel['channel_id'] == channel_id:
            if channel['is_active'] == True:
                raise InputError('An active standup running')
            else:
                threading.Timer(length,stop_send,[auth_user_id,channel_id]).start() #change to false active
                channel['is_active'] = True
                dt = datetime.now()
                timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
                channel['time_finish'] = timestamp + length
    return {'time_finish':channel['time_finish']}

def standup_active(token, channel_id):
    '''
    return standup is active in it, and what time the standup finishes
    
    Arguments:
        token(string) - the token of an user
        channel_id(int) - the id of a channel
        
    Exceptions:
        InputError 
        - Occurs when channel_id is not valid id in data_store
        AccessError
        - Occurs when channel_id is valid and the authorised user is not a member of the channel
    
    Return Value:
        Returns is active and the time finish(the standup)
    '''
    auth_user_id = token_to_id(token)
    data = data_store.get()
    channels = data['channels']


    if valid_channel(data['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
    
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user(auth_user_id, channel['all_members']) == False:
                raise AccessError('Unauthorised user')
            else:
                is_active = channel['is_active']
                time_finish = channel['time_finish']

    return{
        'is_active':is_active,
        'time_finish':time_finish
    }


def standup_send(token, channel_id, message):
    '''
    send message to a standup into the channel given valid token, channel_id and message
    
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
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()
    users = store['users']
    channels = store['channels']

    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user(auth_user_id, channel['all_members']) == False:
                raise AccessError('Unauthorised user')

    # check if channel_id is valid
    if valid_channel(store['channels'],channel_id) == False:
        raise InputError("Invalid channel id")
    
    if len(message) == 0 or len(message) > 1000:
        raise InputError("does not match the required length")
    
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if channel['is_active'] == False:
                raise InputError('An active standup not running')
            else:
                create_standup(auth_user_id,users,message,channel_id)
    return {
    }

#change and store standup messages
def create_standup(auth_user_id,users,message,channel_id):
    data = data_store.get()
    channels = data['channels']

    handle = ''
    for user in users:
        if user['user_id'] == auth_user_id:
            handle = user['handle']
            
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if channel['standups']== '':
                channel['standups'] = handle + ': '+ message
            else:
                channel['standups'] += '\n' + handle + ': '+ message 
    
