from src.data_store import data_store
from src.channels import token_to_id
from src.error import InputError
from src.error import AccessError

def users_all(token):
    '''
    list all the users
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
    
    Return Value:
        Returns a dictionary which conatains the information of all users
    '''
    token_to_id(token)
    store = data_store.get()
    users_list = []
    for user in store['users']:
        users_list.append({
            'u_id': user['user_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle'],
            'profile_img_url': user['profile_img_url'],
        })
    return {
        'users': users_list
    }
'''
Dictionary of shape {
     channels_exist: [{num_channels_exist, time_stamp}], 
     dms_exist: [{num_dms_exist, time_stamp}], 
     messages_exist: [{num_messages_exist, time_stamp}], 
     utilization_rate 
    }
'''