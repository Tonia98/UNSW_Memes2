from src.data_store import data_store
import requests
import re
from src.config import url, SECRET
import jwt
from src.error import AccessError

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

def user_stats(token):
    '''
    get status of user
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains user status
    '''
    # Initial value.
    store = data_store.get()
    auth_user_id = token_to_id(token)
    channel_time = []
    dms_time = []
    msgs_time = []
    # variable that used to build return dictionary
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            num_channels_joined = user['user_stats']['channels_joined'][-1]['num_channels_joined']
            num_dms_joined = user['user_stats']['dms_joined'][-1]['num_dms_joined']
            num_messages_sent = user['user_stats']['messages_sent'][-1]['num_messages_sent']

            for cha_stamp in user['user_stats']['channels_joined']:
                channel_time.append(cha_stamp)

            for dm_stamp in user['user_stats']['dms_joined']:      
                dms_time.append(dm_stamp)
            
            for msg_stamp in user['user_stats']['messages_sent']:
                msgs_time.append(msg_stamp)

    # variable that used to calculate involvement rate
    num_channels = store['workspace_stats']['channels_exist'][-1]['num_channels_exist']
    num_dms = store['workspace_stats']['dms_exist'][-1]['num_dms_exist']
    num_msgs = store['workspace_stats']['messages_exist'][-1]['num_messages_exist']

    # If the denominator is 0, involvement should be 0. 
    # The user's involvement, as defined by this pseudocode: 
    # sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_channels, num_dms, num_msgs)
    if num_channels + num_dms + num_msgs == 0:
        involvement_rate = 0    
    else:
        involvement_rate = (num_channels_joined + num_dms_joined + num_messages_sent) / (num_channels + num_dms + num_msgs)
    # If the involvement is greater than 1, it should be capped at 1.
    if involvement_rate > 1:
        involvement_rate = 1

    return {
        "user_stats": {
            "channels_joined": channel_time,
            "dms_joined": dms_time,
            "messages_sent": msgs_time,
            "involvement_rate": involvement_rate
        }
    }

def users_stats(token):
    '''
    get status of the stream
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains stream status
    '''
    store = data_store.get()
    token_to_id(token)
    channel_time = []
    dms_time = []
    msgs_time = []
    
    # variable that used to calculate utilization rate
    num_user = 0
    user_joined = 0

    for user in store['users']:
        count = False
        num_user = num_user + 1
        for channel in store['channels']:    
            for user_id in channel['all_members']:
                if user_id == user['user_id']:
                    count = True
        
        for dm in store['dms']:
            for user_id in dm['members']:
                if user_id == user['user_id']:
                    count = True
            
        if count == True:
            user_joined = user_joined + 1
        
    # num_users_who_have_joined_at_least_one_channel_or_dm / num_users
    # If the denominator is 0, involvement should be 0. If the involvement is greater than 1, it should be capped at 1.
        utilization_rate = user_joined / num_user
    
    for cha_stamp in store['workspace_stats']['channels_exist']:
        channel_time.append(cha_stamp)

    for dm_stamp in store['workspace_stats']['dms_exist']:    
        dms_time.append(dm_stamp)
            
    for msg_stamp in store['workspace_stats']['messages_exist']:
        msgs_time.append(msg_stamp)

    return {
        "workspace_stats": {
            "channels_exist": channel_time,
            "dms_exist": dms_time,
            "messages_exist": msgs_time,
            "utilization_rate": utilization_rate
        }
    }


from src.data_store import data_store
from datetime import timezone, datetime
import math

# add a channel to the user's stats
def user_stats_add_channel(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            # track the number of channel/dm/message before updated
            new_num = user['user_stats']['channels_joined'][-1]['num_channels_joined'] + 1
            dt = datetime.now()
            timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
            user['user_stats']['channels_joined'].append({
                'num_channels_joined': new_num,
                'time_stamp': timestamp
            })
         
# remove a channel to the user's stats   
def user_stats_remove_channel(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            new_num = user['user_stats']['channels_joined'][-1]['num_channels_joined'] - 1
            dt = datetime.now()
            timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
            user['user_stats']['channels_joined'].append({
                'num_channels_joined': new_num,
                'time_stamp': timestamp
            })
          
# add a dm to the user's stats  
def user_stats_add_dm(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            new_num = user['user_stats']['dms_joined'][-1]['num_dms_joined'] + 1
            dt = datetime.now()
            timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
            user['user_stats']['dms_joined'].append({
                'num_dms_joined': new_num,
                'time_stamp': timestamp
            })
            
# remove a dm to the user's stats
def user_stats_remove_dm(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            new_num = user['user_stats']['dms_joined'][-1]['num_dms_joined'] - 1
            dt = datetime.now()
            timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
            user['user_stats']['dms_joined'].append({
                'num_dms_joined': new_num,
                'time_stamp': timestamp
            })
          
# add a message to the user's stats
def user_stats_add_message(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            new_num = user['user_stats']['messages_sent'][-1]['num_messages_sent'] + 1
            dt = datetime.now()
            timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
            user['user_stats']['messages_sent'].append({
                'num_messages_sent': new_num,
                'time_stamp': timestamp
            })
            
# add a channel to the stream's stats
def stream_stats_add_channel():
    store = data_store.get()
    new_num = store['workspace_stats']['channels_exist'][-1]['num_channels_exist'] + 1
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    store['workspace_stats']['channels_exist'].append({
        'num_channels_exist': new_num,
        'time_stamp': timestamp
    })
    
# add a dm to the stream's stats
def stream_stats_add_dm():
    store = data_store.get()
    new_num = store['workspace_stats']['dms_exist'][-1]['num_dms_exist'] + 1
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    store['workspace_stats']['dms_exist'].append({
        'num_dms_exist': new_num,
        'time_stamp': timestamp
    })
    
# remove a dm to the stream's stats
def stream_stats_remove_dm():
    store = data_store.get()
    new_num = store['workspace_stats']['dms_exist'][-1]['num_dms_exist'] - 1
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    store['workspace_stats']['dms_exist'].append({
        'num_dms_exist': new_num,
        'time_stamp': timestamp
    })
    
# add a message to the stream's stats
def stream_stats_add_message():
    store = data_store.get()
    new_num = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] + 1
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    store['workspace_stats']['messages_exist'].append({
        'num_messages_exist': new_num,
        'time_stamp': timestamp
    })
    
# remove a message to the stream's stats
def stream_stats_remove_message():
    store = data_store.get()
    new_num = store['workspace_stats']['messages_exist'][-1]['num_messages_exist'] - 1
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    store['workspace_stats']['messages_exist'].append({
        'num_messages_exist': new_num,
        'time_stamp': timestamp
    })
            
            
            
