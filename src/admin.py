from src.data_store import data_store
from src.channels import token_to_id
from src.error import InputError
from src.error import AccessError
from src.config import url

# given a user id, return the user's permission_id
def id_to_permission(auth_user_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            return user['permission']

# check if a user id refers to a valid id
def check_uid_validity(u_id):
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == u_id:
            return
    raise InputError("Uid is not valid")

# check if the user is the only global owner and is being demoted to a global member
def check_only_global(u_id, permission_id):
    store = data_store.get()
    # count total the number of global owners
    global_count = 0
    for user in store['users']:
        if user['permission'] == 1:
            global_count += 1
    if global_count == 1 and id_to_permission(u_id) == 1 and permission_id == 2:
        raise InputError("Uid is the only global owner and is demoted to a member")

def userpermission_change(token, u_id, permission_id):
    '''
    change the permission of a sepcific user
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        u_id(int) - the id of the user to be changed the permission
        permission_id(int) - the id of permission(1 represents global owner, 2 represents global member)
        
    Exceptions:
        AccessError - Occurs when token not valid
        AccessError - Occurs when the auth user is not a global owner
        InputError - Occurs when uid does not refer to a valid user
        InputError - Occurs when if uid is the only global owner and is being demoted to a global member
        InputError - Occurs when the permission_id is not valid
    
    Return Value:
        Returns an empty dictionary
    '''
    auth_user_id = token_to_id(token)
    if id_to_permission(auth_user_id) != 1:
        raise AccessError("Auth_user is not a global owner")
    if permission_id != 1 and permission_id != 2:
        raise InputError("Permission id is not valid")
    check_uid_validity(u_id)
    check_only_global(u_id, permission_id)
    # if all the cases are valid
    # set the permission_id
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == u_id:
            user['permission'] = permission_id
    return {}

def user_remove(token, u_id):
    '''
    remove a user from the stream
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        u_id(int) - a user ready to be removed
        
    Exceptions:
        AccessError - Occurs when token not valid
        AccessError - Occurs when the auth user is not a global owner
        InputError - Occurs when uid does not refer to a valid user
        InputError - Occurs when if uid is the only global owner
    
    Return Value:
        Returns an empty dictionary
    '''
    auth_user_id = token_to_id(token)
    if id_to_permission(auth_user_id) != 1:
        raise AccessError("Auth_user is not a global owner")
    check_uid_validity(u_id)
    # use the previous function and set input permission is 2, which is equivalent to checking only global owner
    check_only_global(u_id, 2)
    store = data_store.get()
    # remove the user from the user database
    for user in store['users']:
        if user['user_id'] == u_id:
            store['users'].remove(user)
            store['removed_users'].append({
                'user_id': user['user_id'],
                'email': user['email'],
                'password': user['password'],
                'name_first': 'Removed',
                'name_last': 'user',
                'handle': user['handle'],
                'permission': user['permission'],
                'session_ids': [],
                'profile_img_url': user['profile_img_url']
            })
    for channel in store['channels']:
        # remove the user if he is any channel's owner
        if u_id in channel['owner_members']:
            channel['owner_members'].remove(u_id)
        # remove the user if he is in any channel
        if u_id in channel['all_members']:
            channel['all_members'].remove(u_id)
        # change the removed user's all messages in all channels to 'Removed user'
        for message in channel['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'    
    for dm in store['dms']:
        # remove the user if he is any dm's creator
        if dm['creator'] == u_id:
            dm['creator'] = 0
        # remove the user if he is in any dm
        if u_id in dm['members']:
            dm['members'].remove(u_id)
        # change the removed user's all messages in all dms to 'Removed user'     
        for message in dm['messages']:
            if message['u_id'] == u_id:
                message['message'] = 'Removed user'
    
    return {}

