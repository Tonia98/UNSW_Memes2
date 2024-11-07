from src.channels import token_to_id
from src.data_store import data_store
from src.error import InputError

def search(token, query_str):
    '''
    Given a query string, return a collection of 
    messages in all of the channels/DMs that the user has joined that contain the query.
    
    Arguments:
        token(string) - an encoded string contains the user_id of a user
        
    Exceptions:
        AccessError - Occurs when token not valid
        InputError - Occurs when the length of query_str is less than 1 or over 1000 characters
    
    Return Value:
        Returns a list of messages
    '''
    # Check InputError when: length of query_str is less than 1 or over 1000 characters
    if (len(query_str) < 1 or len(query_str) > 1000):
        raise InputError("length of query_str is less than 1 or over 1000 characters")

    auth_user_id = token_to_id(token)
    message_list = []
    # importing a Database
    store = data_store.get()
    for channel in store["channels"]:
        for user_id in channel["all_members"]:
            # Find channels that the user has joined
            if auth_user_id == user_id:
                # Find messages that contain the query.
                for message in channel["messages"]:
                    if query_str in message["message"]:
                        message_information = {
                        'message_id': message['message_id'],
                        'u_id': message['u_id'],
                        'message': message['message'],
                        'time_created': message['time_created'],
                        'reacts': message['reacts'],
                        'is_pinned': message['is_pinned']
                        }
                        message_list.append(message_information)

    for each_dm in store["dms"]:
        for member_id in each_dm["members"]:
            # Find dm that the user has joined
            if auth_user_id == member_id:
                # Find messages that contain the query.
                for message in each_dm["messages"]:
                    if query_str in message["message"]:
                        message_information = {
                        'message_id': message['message_id'],
                        'u_id': message['u_id'],
                        'message': message['message'],
                        'time_created': message['time_created'],
                        'reacts': message['reacts'],
                        'is_pinned': message['is_pinned']
                        }
                        message_list.append(message_information)
    return message_list