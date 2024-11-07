from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.config import url, SECRET
from src.channels import token_to_id
from src.config import url
import re
import jwt
from src.stats import *

from src.notifications import notification_add

# ------------------------------------- <dm_create> ----------------------------------------
# check if a u_id is valid
def check_valid_user(u_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == u_id:
            return
    raise InputError("Invalid u_id")

# given a user id, get the user's handle
def get_handle(u_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == u_id:
            return user['handle']

def dm_create(token, uids):
    '''
    create a dm
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        uids(list) - a list of integers representing the user ids of the dm's members
        
    Exceptions:
        AccessError - Occurs when token not valid
        InputError - Occurs when any uid in uids is not valid
    
    Return Value:
        Returns a dictionary which conatains dm_id of the dm
    '''
    auth_user_id = token_to_id(token)
    # check if all uid in uids are valid
    for uid in uids:
        check_valid_user(uid)
    store = data_store.get()
    # assign the dm a correct id
    dm_id = store['dm_id_tracker']
    store['dm_id_tracker'] += 1
    # insert the creator's id into the uids
    uids.insert(0, auth_user_id)
    # update the stats of each member in the dm
    for ID in uids:
        user_stats_add_dm(ID)
    stream_stats_add_dm()
    # transform the list of uids into a list of handles 
    # sort alphabetically and join with ', ' to get the dm_name
    handles = [get_handle(uid) for uid in uids]
    handles.sort()
    dm_name = ', '.join(handles)
    store['dms'].append({
        'dm_id': dm_id,
        'dm_name': dm_name,
        'creator': auth_user_id,
        'members': uids,
        'messages': [],
    })
    # update the notifications of each members except the creator
    for ID in uids[1:]:
        notification_add(ID, auth_user_id, -1, dm_id)
    return {
        'dm_id': dm_id
    }

# ------------------------------------- <dm_list> ----------------------------------------
def dm_list(token):
    '''
    list all the dms the token is part of
    
    Arguments:
        token(string) - an encoded string contains the user_id and session_id of an user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains a list of dictionaries of dms that the token is part of
    '''
    auth_user_id = token_to_id(token)
    store = data_store.get()
    dm_list = []
    # loop through every dms
    for dm in store['dms']:
        # loop through every dm's member
        for user_id in dm['members']:
            if user_id == auth_user_id:
                dm_list.append({
                    'dm_id': dm['dm_id'],
                    'name': dm['dm_name'],
                })
                break
    return {
        'dms': dm_list
    }

# ------------------------------------- <dm_details> ----------------------------------------
#check if the dm_id exists in the data_store

#check if the user is a member of the dm
def check_auth_user(user, members):
    if user in members:
        return True
    return False

# transform the dictionary of a user in data store
# to the format matching the output of the dm_details
def transform_user(user):
    return {
        'u_id':user['user_id'],
        'email':user['email'],
        'name_first':user['name_first'],
        'name_last':user['name_last'],
        'handle_str':user['handle'],
        'profile_img_url':user['profile_img_url']
    }

# transform the dictionary of a dm in data store
# to the format matching the output of the dm_details
def transform_dm(dm):
    data = data_store.get()
    members = []
    for user in data['users']:
        if user['user_id'] in dm['members']:
            members.append(transform_user(user))
            
    return {
        'name': dm['dm_name'],
        'members':members
    }

def dm_details(token, dm_id):
    '''
    use dm_id and token to provide basic details about the dm 

    Arguments:
        token(string) - an encoded string contains the user_id and session_id of an user
        dm_id(int) - the id of a dm
        
    Exceptions:
        InputError - Occurs when dm_id is not valid(not in the data store)
        AccessError - Occurs when dm_id is valid and the authorised user is not a member of the dm

    Return Value:
        Returns a dictionary which contains basic details about the dm
    '''

    auth_user_id = token_to_id(token)
    data1 = data_store.get()
    #test valid dm
    if valid_dm(data1['dms'],dm_id) == False:
        raise InputError("Invalid dm")
    # loop through to find the targeted channel
    for dm in data1['dms']:
        if dm['dm_id'] == dm_id:
            if check_auth_user(auth_user_id, dm['members']) == False:
                raise AccessError('Unauthorised user')
            else:
                dm_details = transform_dm(dm)
            return dm_details




# ------------------------- < dm message > ----------------------------

def dm_messages(token, dm_id, start):
    
    '''
    Read at most 50 messages from 'start' index for user in a particular dm
    
    Arguments:
        auth_user_id(int) - the id of an user
        dm_id(int) - the id of a dm
        start(int) - starting position of reading messages in data_store (from most recent message)
        
    Exceptions:
        InputError 
        - Occurs when dm_id is not valid id in data_store
        - Occurs when 'start' index is greater than the numebr of messages in data_store
        AccessError
        - Occurs when dm_id is valid and the authorised user is not a member of the dm
    
    Return Value:
        Returns a list of dictionaries of messages being read from the starting index alongside with
        the position of starting and ending index
    '''
    
    store = data_store.get()
    dms = store['dms']

    auth_user_id = token_to_id(token)
    # creating empty list for returning message dictionary
    dm_list = {}
    
    # loop through every dm in data_store
    for dm in dms:
        # find the matching dm in data_store with input dm_id from the user
        if dm['dm_id'] == dm_id:
            # check if user_id belongs to the given dm_id
            if auth_user_id not in dm['members']:
                raise AccessError("Valid dm_id but invalid user_id")

            # check if start_index is bigger than the number of message stored in data_store
            if (start > len(dm['messages'])):
                raise InputError("Invalid starting postion")
            
            # import list of messages from transform_dict founction
            dm_list = transform_dict(auth_user_id, dm, start)
    
    # check if dm_id is valid
    if valid_dm(store['dms'],dm_id) == False:
        raise InputError("Invalid dm id")
        
    return dm_list

def transform_dict(auth_user_id, dm, start):
    '''
    transform the message's dictionary stored in the data store (empty list)
    to the output form dm_messages() function
    
    Arguments:
        dm(messages) - a dictionary contains 
        messages:{
            'message_id'
            'u_id'
            'message'
            'time_created'
            'is_pinned'
        }
        'start'
    
    
    Return Value:
        Returns a dictionary contains 'messages', 'start' and 'end'
    '''

    new_dm_list = []
    # access message form dm in data_store
    dm_messages = dm['messages']
    
    start_id = start
    i = 1
    while i <= 50:
        # check if least recent message is being read
        if start_id == len(dm['messages']):
            break
        
        dm_messages[start_id]['reacts'][0]['is_this_user_reacted'] = False
        if auth_user_id in dm_messages[start_id]['reacts'][0]['u_ids']:
            dm_messages[start_id]['reacts'][0]['is_this_user_reacted'] = True
        # append message from the most recent to the least bewteen start_id and start_id + 50
        new_dm_list.append(dm_messages[start_id])
        start_id += 1
        i += 1
    # if not all messages are read
    if len(dm['messages']) >= start + 50:
        end = start + 50
    # if most recent messages have been read
    else:
        end = -1
   
    # eturn message_list
    return {
        'messages': new_dm_list,
        'start': start,
        'end': end,
    }

                
            
def dm_leave(token, dm_id):
    '''
    <Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist if this happens. 
    This does not update the name of the DM.>

Arguments:
    <token> (string) - an encoded string contains the user_id of a user
    <dm_id> (integer)    - the id of a dm


Exceptions:
    InputError  - dm_id does not refer to a valid DM

    AccessError - dm_id is valid and the authorised user is not a member of the DM
    
Return Value:
    Returns {}
    '''
    # Seek auth_user_id
    auth_user_id = token_to_id(token)

    valid_dm = False
    dm_member = False

    # importing a Database
    store = data_store.get()

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            valid_dm = True
            for member in dm['members']:
                if auth_user_id == member:
                    dm_member = True

    # Do Access Error Checking
    # (An Access error is checked first because it has a higher priority than an input error)
    if (valid_dm == True and dm_member == False):
        raise AccessError("dm_id is valid and the authorised user is not a member of the DM")

    # Do Input Error Checking
    if valid_dm == False:
        raise InputError("dm_id does not refer to a valid DM")

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm['members'].remove(auth_user_id)
            user_stats_remove_dm(auth_user_id)
            if auth_user_id == dm['creator']:
                dm['creator'] = 0 

# ------------------------------------- <dm_remove> ----------------------------------------
def valid_dm(dms, dm_id):
    for dm in dms:
        if dm['dm_id'] == dm_id:
            return True
    return False

#check if the user is a member of the dm
def auth_user(user, creator):
    if user == creator:
        return True
    return False

def dm_remove(token, dm_id):
    '''
    remove all memebers from an existing DM
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        dm_id(int) - a dm ready to be removed
        
    Exceptions:
        InputError - Occurs when dm_id is not valid(not in the data store)
        AccessError - Occurs when dm_id is valid and the authorised user is not a member of the dm
    
    Return Value:
        Returns an empty dictionary
    '''
    auth_user_id = token_to_id(token)
    data1 = data_store.get()
    #test valid dm
    if valid_dm(data1['dms'],dm_id) == False:
        raise InputError("Invalid dm")
    
    # loop through to find the targeted dm
    for dm in data1['dms']:
        if dm['dm_id'] == dm_id:
            if auth_user(auth_user_id, dm['creator']) == False:
                raise AccessError('Unauthorised user')
            for ID in dm['members']:
                user_stats_remove_dm(ID)
            stream_stats_remove_dm()
            data1['dms'].remove(dm)
    return {}
