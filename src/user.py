from src.error import InputError
from src.channels import token_to_id
from src.data_store import data_store
from src.auth import *
from src.config import url
import urllib.request
from PIL import Image
import requests
import os

def user_profile(token, u_id):
    '''
    try to list information of user's(u_id) profile  

    Arguments:
        token (string)     - an encoded string contains the auth_user_id and session_id
        u_id (integer)     - the user whose information of profile will be listed 
        
    Exceptions:
        AccessError - Occurs when token is invalid
        InputError  - Occurs when u_id can not be found
    
    Return Value:
        Returns a dictionary containing user_id, user's email, user's first name 
        and last name and user's handle
    '''
    # check if token is valid
    token_to_id(token)

    store = data_store.get()
    user_data = store['users']

    # list infomation of user profile if u_id can be found in normal exist users' list
    for user in user_data:
        if user['user_id'] == u_id:
            return {'user': {'user_id': u_id, 'email': user['email'], 'name_first': user['name_first'], \
                    'name_last': user['name_last'], 'handle_str': user['handle'], 'profile_img_url': user['profile_img_url']}}

    # list infomation of user profile if u_id can be found in removed users' list
    rmed_users = store['removed_users']
    for rmu in rmed_users:
        if rmu['user_id'] == u_id:
            return {'user': {'user_id': u_id, 'email': rmu['email'], 'name_first': 'Removed', \
                    'name_last': 'user', 'handle_str': rmu['handle'], 'profile_img_url': user['profile_img_url']}}


    raise InputError("user id does not refer to a valid user")

def user_profile_set_name(token, name_first, name_last):
    '''
    try to list information of user's(u_id) profile  

    Arguments:
        token (string)       - an encoded string contains the auth_user_id and session_id
        name_first (string)  - first name of auth_user want to change to
        name_last (string)   - last  name of auth_user want to change to
        
    Exceptions:
        AccessError - Occurs when token is invalid
        InputError  - Occurs when length of first name or last name exceed 50 or empty
    
    Return Value:
        Returns an empty dictionary.
    '''
    auth_user_id = token_to_id(token)

    store = data_store.get()
    user_data = store['users']

    # check if length of first name or last name exceed 50 or empty
    check_valid_name(name_first)
    check_valid_name(name_last)

    # change first name and last name
    for user in user_data:
        if user['user_id'] == auth_user_id:
            user['name_first'] = name_first
            user['name_last'] = name_last

    return {}
            
def user_profile_set_handle(token, handle_str):
    '''
    try to list information of user's(u_id) profile  

    Arguments:
        token (string)       - an encoded string contains the auth_user_id and session_id
        handle_str (string)  - handle that auth_user want to change to
        
    Exceptions:
        AccessError - Occurs when token is invalid
        InputError  - Occurs when length of handle exceed 20 or less than 3
        InputError  - Occurs when hadle contains characters that are not alphanumeric
        InputError  - Occurs when handle is already used by another user

    Return Value:
        Returns an empty dictionary
    '''
    auth_user_id = token_to_id(token)

    store = data_store.get()
    user_data = store['users']

    # check if length of handle exceed 20 or less than 3
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("length of handle is not between 3 and 20 characters inclusive")

    # check if hadle contains characters that are not alphanumeric
    for c in handle_str:
        if not (c.isalpha() or c.isnumeric()):
            raise InputError('handle contains characters that are not alphanumeric')

    # check if handle is already used by another user
    for user in user_data:
        if user['handle'] == handle_str:
            raise InputError('the handle is already used by another user')
    
    # change handle if every thing goes fine    
    for user in user_data:
        if user['user_id'] == auth_user_id:
            user['handle'] = handle_str
    return {}

#------------------------------------ <user_profile_set_email> ----------------------------------------


def user_profile_set_email(token, email):
    '''
    change the users' email address  

    Arguments:
        token (string)       - an encoded string contains the auth_user_id and session_id
        email (string)       - user's email address
        
    Exceptions:
        InputError  - Occurs when email entered is not a valid email
        InputError  - Occurs when email address is already being used by another user

    Return Value:
        Returns an empty dictionary
    '''
    store = data_store.get()
    user_data = store['users']
    auth_user_id = token_to_id(token)

    check_valid_email(email)
    for user in user_data:
        if user['user_id'] == auth_user_id:
            user['email'] = email
    return {}
    
def uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    change the users' email address  

    Arguments:
        token (string)       - an encoded string contains the auth_user_id
        img_url (string)       - an url linked to an image
        x_start(integer)       - the start position of the width of the image after cropped
        y_start(integer)       - the start position of the height of the image after cropped
        x_end(integer)       - the end position of the width of the image after cropped
        y_end(integer)       - the end position of the height of the image after cropped
        
    Exceptions:
        AccessError - Occurs if the token does not refer to an active session
        InputError  - Occurs when img_url is not a valid url
        InputError  - Occurs when x_start, y_start, x_end or y_end exceed the size of the image
        InputError  - Occurs when x_start > x_end or y_start > y_end
        InputError  - Occurs when the image uploaded is not jpg

    Return Value:
        Returns an empty dictionary
    '''
    auth_user_id = token_to_id(token)
    # try to access the image url and store it as image + user_id + .jpg
    try:
        urllib.request.urlretrieve(img_url, f'src/static/image{auth_user_id}.jpg')
    except ValueError as exception:
        raise InputError("img_url returns an HTTP status other than 200") from exception
    img = requests.head(img_url)
    # check if the img_url is jpg
    if img.headers['content-type'] not in ("image/jpeg", "image/jpg"):
        os.remove(f'src/static/image{auth_user_id}.jpg')
        raise InputError("Image uploaded is not a JPG")
    
    if x_end < x_start or y_end < y_start:
        raise InputError('x_end is less than x_start or y_end is less than y_start')
    
    imageobject = Image.open(f'src/static/image{auth_user_id}.jpg')
    if x_end > imageobject.width or y_end > imageobject.height:
        raise InputError('Any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL')
    
    # crop the image and store it
    cropped = imageobject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f'src/static/image{auth_user_id}.jpg')
    
    # store the server url to user profile
    store = data_store.get()
    for user in store['users']:
        if user['user_id'] == auth_user_id:
            user['profile_img_url'] = url + f'static/image{auth_user_id}.jpg'
    
    return {}
