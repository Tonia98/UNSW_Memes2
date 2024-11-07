import requests
import json

from werkzeug.exceptions import LengthRequired
from src.config import url
#######################  functions to wrap normal functions for tests ##########
'''
These functions send the server a post request,
then return status code of the response if caller need status code, 
else return the dictionary as spec mentioned.
'''
#################### auth_functions#############################################

def status_code_or_return_value(function):
    def wrapper(need_status_code, *args, **kwargs):
        if need_status_code:
            return function(need_status_code, *args, **kwargs).status_code
        else:
            return function(need_status_code, *args, **kwargs).json()
    return wrapper

@status_code_or_return_value
def wrap_auth_register(need_status_code, email, password, name_first, name_last):
    arguments = {'email': email, 'password': password, 'name_first': name_first, 'name_last': name_last}
    return requests.post(url + 'auth/register/v2', json=arguments)
    

@status_code_or_return_value
def wrap_auth_login(need_status_code, email, password):
    arguments = {'email': email, 'password': password}
    return requests.post(url + 'auth/login/v2', json=arguments)
    

@status_code_or_return_value
def wrap_auth_logout(need_status_code, token):
    return requests.post(url + 'auth/logout/v1', json={'token': token})
    
        
@status_code_or_return_value
def wrap_auth_passwordreset_request(need_status_code, email):
    return requests.post(url + 'auth/passwordreset/request/v1', json={'email': email})
    
        
@status_code_or_return_value
def wrap_auth_passwordreset_reset(need_status_code, reset_code, new_password):
    return requests.post(url + 'auth/passwordreset/reset/v1', json={'reset_code': reset_code, 'new_password': new_password})
    
############################ channel functions ##################################
@status_code_or_return_value
def wrap_channel_details(need_status_code, token, channel_id):
    arguments = {'token': token, 'channel_id': channel_id}
    return requests.get(url + 'channel/details/v2', params=arguments)
    

@status_code_or_return_value
def wrap_channel_invite(need_status_code, token, channel_id, u_id):
    arguments = {'token': token, 'channel_id': channel_id, 'u_id': u_id} 
    return requests.post(url + 'channel/invite/v2', json=arguments)
    

@status_code_or_return_value
def wrap_channel_join(need_status_code, token, channel_id):
    arguments = {'token': token, 'channel_id': channel_id} 
    return requests.post(url + 'channel/join/v2', json=arguments)
    
        
@status_code_or_return_value
def wrap_channel_removeowner(need_status_code, token, channel_id, u_id):
    arguments = {'token': token, 'channel_id': channel_id, 'u_id': u_id} 
    return requests.post(url + 'channel/removeowner/v1', json=arguments)
    

@status_code_or_return_value
def wrap_channel_messages(need_status_code, token, channel_id, start):
    arguments = {'token': token, 'channel_id': channel_id, 'start': start}
    return requests.get(url + 'channel/messages/v2', params=arguments)
    

@status_code_or_return_value
def wrap_channel_addowner(need_status_code, token, channel_id, u_id):
    arguments = {'token': token, 'channel_id': channel_id, 'u_id': u_id} 
    return requests.post(url + 'channel/addowner/v1', json=arguments)
    

@status_code_or_return_value
def wrap_channel_leave(need_status_code, token, channel_id):
    arguments = {'token': token, 'channel_id': channel_id} 
    return requests.post(url + 'channel/leave/v1', json=arguments)
    

#######################  channels functions ####################################
@status_code_or_return_value
def wrap_channels_create(need_status_code, token, name, is_public):
    arguments = {'token': token, 'name': name, 'is_public': is_public}
    return requests.post(url + 'channels/create/v2', json=arguments)
    

@status_code_or_return_value
def wrap_channels_list(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'channels/list/v2', params=arguments)
    
        
@status_code_or_return_value
def wrap_channels_listall(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'channels/listall/v2', params=arguments)
    


####################### dm functions #############################################
@status_code_or_return_value
def wrap_dm_create(need_status_code, token, uids):
    arguments = {'token': token, 'u_ids': uids}
    return requests.post(url + 'dm/create/v1', json=arguments)
    

@status_code_or_return_value
def wrap_dm_list(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'dm/list/v1', params=arguments)
    

@status_code_or_return_value
def wrap_dm_details(need_status_code, token, dm_id):
    arguments = {'token': token, 'dm_id':dm_id}
    return requests.get(url + 'dm/details/v1', params=arguments)
    

@status_code_or_return_value
def wrap_dm_remove(need_status_code, token, dm_id):
    arguments = {'token': token, 'dm_id': dm_id}
    return requests.delete(url + 'dm/remove/v1', json=arguments)
    

@status_code_or_return_value
def wrap_dm_messages(need_status_code, token, dm_id, start):
    arguments = {'token': token, 'dm_id': dm_id, 'start': start}
    return requests.get(url + 'dm/messages/v1', params=arguments)
    


@status_code_or_return_value
def wrap_dm_leave(need_status_code, token, dm_id):
    arguments = {'token': token, 'dm_id': dm_id}
    return requests.post(url + 'dm/leave/v1', json=arguments)
    
    
###################################### user profile functions ##################
@status_code_or_return_value
def wrap_user_profile(need_status_code, token, u_id):
    return requests.get(url + 'user/profile/v1', params={'token': token, 'u_id': u_id})
    

@status_code_or_return_value
def wrap_user_profile_set_name(need_status_code, token, name_first, name_last):
    arguments = {'token': token, 'name_first': name_first, 'name_last': name_last}
    return requests.put(url + 'user/profile/setname/v1', json=arguments)
    

@status_code_or_return_value
def wrap_user_profile_set_handle(need_status_code, token, handle_str):
    arguments = {'token': token, 'handle_str': handle_str}
    return requests.put(url + 'user/profile/sethandle/v1', json=arguments)
    

@status_code_or_return_value
def wrap_user_profile_set_email(need_status_code, token, email):
    arguments = {'token': token, 'email': email}
    return requests.put(url + 'user/profile/setemail/v1', json=arguments)
    
@status_code_or_return_value
def wrap_uploadphoto(need_status_code, token, img_url, x_start, y_start, x_end, y_end):
    arguments = {'token': token, 'img_url': img_url, 'x_start': x_start, 'y_start': y_start, 'x_end': x_end, 'y_end': y_end}
    return requests.post(url + 'user/profile/uploadphoto/v1', json=arguments)

################################# message functions###########################
@status_code_or_return_value
def wrap_message_send(need_status_code, token, channel_id, message):
    arguments = {'token':token, 'channel_id': channel_id, 'message': message}
    return requests.post(url + 'message/send/v1', json=arguments)
    

@status_code_or_return_value
def wrap_message_edit(need_status_code, token, message_id, message):
    arguments = {'token':token, 'message_id': message_id, 'message': message}
    return requests.put(url + 'message/edit/v1', json=arguments)
    

@status_code_or_return_value
def wrap_message_remove(need_status_code, token, message_id):
    arguments = {'token': token, 'message_id': message_id}
    return requests.delete(url + 'message/remove/v1', json=arguments)
    

@status_code_or_return_value
def wrap_message_senddm(need_status_code, token, dm_id, message):
    arguments = {'token':token, 'dm_id': dm_id, 'message': message}
    return requests.post(url + 'message/senddm/v1', json=arguments)


@status_code_or_return_value
def wrap_message_pin(need_status_code, token, message_id):
    return requests.post(url + 'message/pin/v1', json={'token': token, 'message_id': message_id})

@status_code_or_return_value
def wrap_message_unpin(need_status_code, token, message_id):
    return requests.post(url + 'message/unpin/v1', json={'token': token, 'message_id': message_id})

@status_code_or_return_value
def wrap_message_sendlater(need_status_code, token, channel_id, message, time_sent):
    arguments = {'token': token, 'channel_id': channel_id, 'message': message, 'time_sent': time_sent}
    return requests.post(url + 'message/sendlater/v1', json=arguments)

@status_code_or_return_value
def wrap_message_sendlaterdm(need_status_code, token, dm_id, message, time_sent):
    arguments = {'token': token, 'dm_id': dm_id, 'message': message, 'time_sent': time_sent}
    return requests.post(url + 'message/sendlaterdm/v1', json=arguments)

@status_code_or_return_value
def wrap_message_share(need_status_code, token, og_message_id, message, channel_id, dm_id):
    arguments = {'token':token, 'og_message_id':og_message_id, 'message':message, 'channel_id':channel_id, 'dm_id':dm_id}
    return requests.post(url + 'message/share/v1', json=arguments)

@status_code_or_return_value
def wrap_message_react(need_status_code, token, message_id, react_id):
    arguments = {'token':token, 'message_id': message_id, 'react_id': react_id}
    return requests.post(url + 'message/react/v1', json=arguments)

@status_code_or_return_value
def wrap_message_unreact(need_status_code, token, message_id, react_id):
    arguments = {'token':token, 'message_id': message_id, 'react_id': react_id}
    return requests.post(url + 'message/unreact/v1', json=arguments)
############################### user all functions ############################# 
@status_code_or_return_value
def wrap_users_all(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'users/all/v1', params=arguments)
    
############################# admin functions###################################
@status_code_or_return_value
def wrap_userpermission_change(need_status_code, token, u_id, permission_id):
    arguments = {'token': token, 'u_id': u_id, 'permission_id': permission_id}
    return requests.post(url + '/admin/userpermission/change/v1', json=arguments)
    
@status_code_or_return_value
def wrap_user_remove(need_status_code, token, u_id):
    arguments = {'token': token, 'u_id': u_id}
    return requests.delete(url + '/admin/user/remove/v1', json=arguments)

############################# stats functions###################################
@status_code_or_return_value
def wrap_user_stats(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'user/stats/v1', params=arguments)

@status_code_or_return_value
def wrap_users_stats(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'users/stats/v1', params=arguments)

@status_code_or_return_value
def wrap_notifications_get(need_status_code, token):
    arguments = {'token': token}
    return requests.get(url + 'notifications/get/v1', params=arguments)

@status_code_or_return_value
def wrap_search(need_status_code, token, query_str):
    arguments = {'token': token, 'query_str': query_str}
    return requests.get(url + 'search/v1', params=arguments)

############################# standup functions###################################
@status_code_or_return_value
def wrap_standup_send(need_status_code, token, channel_id, message):
    arguments = {'token': token, 'channel_id': channel_id, 'message': message}
    return requests.post(url + 'standup/send/v1', json=arguments)

@status_code_or_return_value
def wrap_standup_start(need_status_code, token, channel_id, length):
    arguments = {'token': token, 'channel_id': channel_id, 'length': length}
    return requests.post(url + 'standup/start/v1', json=arguments)

@status_code_or_return_value
def wrap_standup_active(need_status_code, token, channel_id):
    arguments = {'token': token, 'channel_id': channel_id}
    return requests.get(url + 'standup/active/v1', params=arguments)
############################# clear function ###################################
def wrap_clear():
    return requests.delete(url + '/clear/v1', json={}).json()
