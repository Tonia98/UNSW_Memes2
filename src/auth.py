from src.data_store import data_store
from src.error import InputError
import re
from src.config import url, SECRET
import jwt
import hashlib
from src.channels import token_to_id
import imaplib                              
import email
import smtplib
import string
import random
from datetime import timezone, datetime
import math


# check if email has already been taken by other user and
# if email is in correct format
def check_valid_email(email):
    store = data_store.get()
    # check if email is already be taken by another user 
    for user in store['users']:
        if email == user['email']:
            raise InputError("Email address is already being used by another user")

    # check if email match the format
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if(not re.fullmatch(regex, email)):
        raise InputError("Invalid email format")


# check if length of first name or last name exceed 50 or empty
def check_valid_name(name_first_or_last):
    if len(name_first_or_last) < 1 or len(name_first_or_last) > 50:
        raise InputError("Invalid name")

def generate_handle(name_last, name_first):
    full_name = name_first + name_last
    new_handle = ""
    # make sure generated new handle consist of alphabets in lower case or numbers
    for i in full_name:
        if (i.isalpha() or i.isnumeric()) and len(new_handle) < 20:
            new_handle += i.lower()
    
    # generate a number append at the end of handle if handle already excist
    store = data_store.get()
    num = -1
    for user in store['users']:
        if (new_handle in user["handle"]):
            num = 0
            if (new_handle != user["handle"]):
                num = int(user["handle"][len(new_handle):]) + 1
    # add number to the end of handle if needed
    if num != -1:
        new_handle += str(num)
    return new_handle

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# create new user account with inputs
def create_new_account(email, password, name_first, name_last, user_id, session_id):
    new_account = {}
    new_account['user_id'] = user_id
    
    check_valid_email(email)
    new_account['email'] = email

    if len(password) < 6:
        raise InputError("length of password is less than 6 characters")
    else:
        new_account['password'] = hash_password(password) 

    check_valid_name(name_last)
    new_account['name_last'] = name_last
    
    check_valid_name(name_first)
    new_account['name_first'] = name_first
    
    new_account['handle'] = generate_handle(name_last, name_first)
    
    new_account['profile_img_url'] = url + 'static/image.jpg'
    
    # the user's stats start to count
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    new_account['user_stats'] = {
        "channels_joined": [
            {
                "num_channels_joined": 0,
                "time_stamp": timestamp
            }
        ],
        "dms_joined": [
            {
                "num_dms_joined": 0,
                "time_stamp": timestamp
            }
        ],
        "messages_sent": [
            {
                "num_messages_sent": 0,
                "time_stamp": timestamp
            }
        ]
    }
    
    new_account['notifications'] = []
    
    if user_id == 1:
        new_account['permission'] = 1
        store = data_store.get()
        # if the first user registers, the stream's stats start to count
        dt = datetime.now()
        timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
        store['workspace_stats'] = {
            "channels_exist": [
                {
                    "num_channels_exist": 0,
                    "time_stamp": timestamp
                }
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0,
                    "time_stamp": timestamp
                }
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0,
                    "time_stamp": timestamp
                }
            ]
        }
    else:
        new_account['permission'] = 2
    new_account['session_ids'] = [session_id]

    return new_account

# encode user id and session id 
def generate_token(user_id, session_id):
    return jwt.encode({'user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256')

def auth_login(email, password):
    '''
    try to log in a user

    Arguments:
        email (string)        - user's email address
        password (string)     - user's new account password
        
    Exceptions:
        InputError  - Occurs when email entered does not belong to a user
                    - Occurs when password is not correct
    
    Return Value:
        Returns a dictionary containing auth user id and token
    '''
    store = data_store.get()
    user_data = store['users']
    # find the user's email and compare the password
    for user in user_data:
        if email == user["email"]:
            if hash_password(password) == user["password"]:
                session_id = store['session_id_tracker']
                store['session_id_tracker']  += 1
                user['session_ids'].append(session_id)
                return {
                    'token': generate_token(user["user_id"], session_id),
                    'auth_user_id': user["user_id"]
                }
            else:
                raise InputError("Wrong password")
    raise InputError("Email does not belong to a user")


def auth_logout(token):
    '''
    try to log out a user

    Arguments:
        token(string) - an encoded string contains the auth_user_id and session_id
        
    Exceptions:
        AccessError - Occurs when token format is invalid
                    - Occurs when auth_user_id is invalid
                    - Occurs when session id cant be found in given auth_user's session list
    
    Return Value:
        Returns an empty dictionary
    '''
    store = data_store.get()
    user_data = store['users']
    auth_user_id = token_to_id(token)
    session = jwt.decode(token, SECRET, algorithms=['HS256'])
    for user in user_data:
        if user['user_id'] == auth_user_id:
            user['session_ids'].remove(session['session_id'])

    return {}
    
def auth_register(email, password, name_first, name_last):
    '''
    register a new user

    Arguments:
        email (string)        - user's email address
        password (string)     - user's new account password
        name_first (string)   - user's first name
        name_last (string)    - user's last name

    Exceptions:
        InputError  - Occurs when email entered is not a valid email
                    - Occurs when email address is already being used by another user
                    - Occurs when length of password is less than 6 characters
                    - Occurs when length of name_first or name_last is not between 1 and 50 characters inclusive
    
    Return Value:
        Returns a dictionary containing auth user id and token
    '''
    store = data_store.get()
    user_data = store['users']

    user_id = store['user_id_tracker']
    store['user_id_tracker'] += 1

    session_id = store['session_id_tracker']
    store['session_id_tracker'] += 1

    new_user = create_new_account(email, password, name_first, name_last, user_id, session_id)
    user_data.append(new_user)
    return {
        'token': generate_token(user_id, session_id),
        'auth_user_id': user_id
    }
    
# random generate a 8-character string
def generate_random():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def auth_passwordreset_request(email):
    '''
    request a secret code from an email

    Arguments:
        email (string)        - user's email address
    
    Return Value:
        Returns a em empty dictionary
    '''
    # the email of our stream
    sender = "DODOforever2@gmail.com"
    receiver = email
    password = "memodragon"
    # generate a random 8 character string in the subject of the email
    message = 'Subject: {}\n\n{}'.format(generate_random(), 'The subject is your secret code')
    # send the secret code to the user's email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, message)
    # log the user out for all sessions
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email:
            user['session_ids'].clear()
            break
    return {}
    
# given a secret code
# search for the email associated with the code in our stream email
def get_email(code):
    imap = imaplib.IMAP4_SSL('imap.gmail.com',993)
    # access to the sent mail of our stream account
    imap.login("DODOforever2@gmail.com", "memodragon")
    res, messages = imap.select('"[Gmail]/Sent Mail"')#pylint: disable=unused-variable
    # iterate through all sent mail in our stream account from the most recent one
    num_messages = int(messages[0])
    for i in range(num_messages, 0, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")     
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])#pylint: disable=unsubscriptable-object
                # found the code
                # return the associated email
                if msg['Subject'] == code:
                    return msg['Bcc']
    return None
    
def auth_passwordreset_reset(reset_code, new_password):
    '''
    reset the password of a user

    Arguments:
        reset_code (string) - a code entered by the user to verify himself/herself
        new_password (string) - the new password the user wants to change to
    
    Return Value:
        Returns a em empty dictionary
    '''
    email = get_email(reset_code)
    # if the email or the code is not found in sent email by stream email
    if email == None:
        raise InputError("Reset_code is not a valid reset code")
    if len(new_password) < 6:
        raise InputError("Password entered is less than 6 characters long")
    store = data_store.get()
    # reset the password
    for user in store['users']:
        if user['email'] == email:
            user['password'] = hash_password(new_password)
            break
    return {}



